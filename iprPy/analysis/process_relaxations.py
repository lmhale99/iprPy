# coding: utf-8

# Standard Python libraries
from itertools import combinations
from typing import Optional, Tuple
from copy import deepcopy
from uuid import uuid4

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://pandas.pydata.org/
import pandas as pd

from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
from atomman.library.record.RelaxedCrystal import RelaxedCrystal

from potentials.record.BasePotentialLAMMPS import BasePotentialLAMMPS

from ..database.IprPyDatabase import IprPyDatabase
from . import match_reference_prototype, get_isolated_atom_energies

def process_relaxations(database: IprPyDatabase,
                        potential_LAMMPS_key: str,
                        potential_key: str,
                        potential: Optional[BasePotentialLAMMPS] = None,
                        ref_proto_df: Optional[pd.DataFrame] = None,
                        iso_energy_df: Optional[pd.DataFrame] = None, 
                        all_ref_df: Optional[pd.DataFrame] = None,
                        all_evsr_records: Optional[npt.ArrayLike] = None,
                        all_evsr_df: Optional[pd.DataFrame] = None,
                        all_box_df: Optional[pd.DataFrame] = None,
                        all_static_df: Optional[pd.DataFrame] = None,
                        all_dynamic_df: Optional[pd.DataFrame] = None,
                        all_spg_df: Optional[pd.DataFrame] = None,
                        verbose: bool = False):

    # Get the associated LAMMPS potential record
    if potential is None:
        potential = database.potdb.get_lammps_potential(key=potential_LAMMPS_key,
                                                        potkey=potential_key)
        if verbose:
            print('LAMMPS potential record retrieved')

    # Get/select E_vs_r_scan results
    evsr_df = get_evsr_df(database, potential_LAMMPS_key, potential_key,
                          all_evsr_records=all_evsr_records,
                          all_evsr_df=all_evsr_df, verbose=verbose)
    
    # Get/select reference crystals
    ref_df = get_ref_df(database, potential.elements(),
                        all_ref_df=all_ref_df, verbose=verbose)

    # Get/select relax records
    relax_df = get_relax_df(database, potential_LAMMPS_key, potential_key,
                            ref_df, evsr_df, all_box_df=all_box_df,
                            all_static_df=all_static_df,
                            all_dynamic_df=all_dynamic_df, verbose=verbose)

    # Merge in space group information
    relax_df = merge_spg_info(database, relax_df, all_spg_df=all_spg_df, verbose=verbose)
    
    # Identify if structures transformed
    relax_df = identify_transformed(database, relax_df, all_spg_df=all_spg_df)

    # Identify prototype field
    relax_df = identify_prototype(database, relax_df,
                                  ref_proto_df=ref_proto_df,
                                  all_spg_df=all_spg_df)

    # Create any missing relaxed_crystal records
    create_missing_relaxed_crystals(database, relax_df, potential_LAMMPS_key,
                                    potential_key, atom_style=potential.atom_style,
                                    iso_energy_df=iso_energy_df, verbose=verbose)

    # Identify duplicates and update their standing
    identify_duplicates(database, potential_LAMMPS_key, potential_key,
                        verbose=verbose)

    #return relax_df
    
def get_evsr_df(database: IprPyDatabase, 
                potential_LAMMPS_key: str,
                potential_key: str,
                all_evsr_records: Optional[npt.ArrayLike] = None,
                all_evsr_df: Optional[pd.DataFrame] = None,
                verbose: bool = False
                ) -> pd.DataFrame:
    """
    Fetches/builds a dataframe of E_vs_r_scan results for the specified
    potential.
    
    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    potential_LAMMPS_key : str
        The UUID4 associated with the potential implementation.
    potential_LAMMPS_id : str
        The UUID4 associated with the potential model.
    all_evsr_records : Array-Like, optional
        All E_vs_r_scan calculation records.  If not given, a fresh query to
        the database will be performed.
    all_evsr_df : pd.DataFrame, optional
        The metadata for all E_vs_r_scan calculation records.  If not given, a
        fresh query to the database will be performed.

    Raises
    ------
    ValueError
        If no E_vs_r_scan results are found for the potential or if any of the
        E_vs_r_scan calculations for the potential have a status of "not
        calculated".

    Returns
    -------
    evsr_df : pandas.DataFrame
        The E_vs_r_scan metadata for the specified potential with number of min
        cells added in.
    """
    if all_evsr_records is None or all_evsr_df is None:
        evsr_records, evsr_df = database.get_records(style='calculation_E_vs_r_scan',
                                                     potential_key=potential_key,
                                                     potential_LAMMPS_key=potential_LAMMPS_key,
                                                     return_df=True)
    else:
        ix = ((all_evsr_df.potential_key==potential_key) &
              (all_evsr_df.potential_LAMMPS_key==potential_LAMMPS_key))
        evsr_records = all_evsr_records[ix]
        evsr_df = all_evsr_df[ix].reset_index(drop=True)
        
    if len(evsr_df) == 0:
        raise ValueError('No E_vs_r_scan calculations!')
    
    if verbose:
        print(len(evsr_df), 'E_vs_r_scan calculations found')
    
    if sum(evsr_df.status == 'not calculated') > 0:
        raise ValueError('Some E_vs_r_scan calculations not finished!')

    # Get number of min_cells
    num_min_cells = []
    for evsr_record in evsr_records:
        try:
            num_min_cells.append(len(evsr_record.min_cells))
        except:
            num_min_cells.append(0)
    evsr_df['num_min_cells'] = num_min_cells

    return evsr_df
    
def get_ref_df(database: IprPyDatabase,
               elements: list,
               all_ref_df: Optional[pd.DataFrame] = None,
               verbose: bool = False
               ) -> pd.DataFrame:
    """
    Fetches/builds a dataframe of reference_crystal records for the specified
    potential.
    
    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    potential_LAMMPS_key : str
        The UUID4 associated with the potential implementation.
    potential_LAMMPS_id : str
        The UUID4 associated with the potential model.
    all_ref_df : pd.DataFrame, optional
        The metadata for all reference crystal records.  If not given, a fresh
        query to the database will be performed.

    Returns
    -------
    ref_df : pandas.DataFrame
        The reference_crystal metadata for all crystals that have elements that
        are modeled by the potential.
    """
    if all_ref_df is None:
        all_ref_df = database.get_records_df(style='reference_crystal')
    
    def compare_symbols(series, symbols):
        return sorted(list(series.symbols)) == sorted(list(symbols))

    # Get matching refs based on elements/symbols
    indices = []
    for i in range(len(elements)):
        for symbols in combinations(elements, i+1):
            indices.extend(all_ref_df[all_ref_df.apply(compare_symbols, axis=1, args=[symbols])].index)
    ref_df = all_ref_df.loc[sorted(indices)]
    
    # Set dummy empty dataframe if no matches found
    if len(ref_df) == 0:
        ref_df = pd.DataFrame(columns=['id'])
    
    if verbose:
        print(len(ref_df), "reference_crystal records found with the potential's elements")

    return ref_df
            
def get_relax_df(database: IprPyDatabase,
                 potential_LAMMPS_key: str,
                 potential_key: str,
                 ref_df: pd.DataFrame,
                 evsr_df: pd.DataFrame,
                 all_box_df: Optional[pd.DataFrame] = None,
                 all_static_df: Optional[pd.DataFrame] = None,
                 all_dynamic_df: Optional[pd.DataFrame] = None,
                 verbose: bool = False):
    """
    Constructs a combined DataFrame of all relax calculation records for a
    given LAMMPS potential.  This checks the number and status of all involved
    records (relax_box:main, relax_static:main, relax_dynamic:main and
    relax_static:from_dynamic). 
    
    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    potential_LAMMPS_key : str
        The UUID4 associated with the potential implementation.
    potential_LAMMPS_id : str
        The UUID4 associated with the potential model.
    ref_df : pandas.DataFrame
        The metadata for all reference crystals with elements modeled by the
        potential.  Use get_ref_df() to build this.
    evsr_df : pandas.DataFrame
        The metadata for all E_vs_r_scan calculations for the potential.  Use
        get_evsr_df() to build this.
    all_box_df : pandas.DataFrame, optional
        The metadata for all relax_box calculation records.  If not given, a
        fresh query to the database will be performed.
    all_static_df : pandas.DataFrame, optional
        The metadata for all relax_static calculation records.  If not given, a
        fresh query to the database will be performed.
    all_dynamic_df : pandas.DataFrame, optional
        The metadata for all relax_dynamic calculation records.  If not given,
        a fresh query to the database will be performed.

    Raises
    ------
    ValueError
        If any of the relax calculations for the potential have a status of
        "not calculated".

    Returns
    -------
    relax_df : pandas.DataFrame
        The combined relax_box and relax_static results for the potential with
        a "method" field added to indicate the relaxation method.
    """
    ############################# Load box records ############################
    if all_box_df is None:
        box_df = database.get_records_df(style='calculation_relax_box',
                                         branch='main',
                                         potential_key=potential_key,
                                         potential_LAMMPS_key=potential_LAMMPS_key)
    else:
        ix = (
            (all_box_df.branch == 'main') &
            (all_box_df.potential_key == potential_key) &
            (all_box_df.potential_LAMMPS_key == potential_LAMMPS_key))
        box_df = all_box_df[ix].reset_index(drop=True)
    
    if verbose:
        print(len(box_df), 'relax_box:main calculations found')
    
    if sum(box_df.status == 'not calculated') > 0:
        raise ValueError('Some relax_box calculations not finished!')    

    # Check record counts
    check_round1_relax(box_df, ref_df, evsr_df)

    ############################ Load static records ###########################
    if all_static_df is None:
        static_df = database.get_records_df(style='calculation_relax_static',
                                            branch='main',
                                            potential_key=potential_key,
                                            potential_LAMMPS_key=potential_LAMMPS_key)
    else:
        ix = (
            (all_static_df.branch == 'main') &
            (all_static_df.potential_key == potential_key) &
            (all_static_df.potential_LAMMPS_key == potential_LAMMPS_key))
        static_df = all_static_df[ix].reset_index(drop=True)
    
    if verbose:
        print(len(static_df), 'relax_static:main calculations found')
    
    if sum(static_df.status == 'not calculated') > 0:
        raise ValueError('Some relax_static calculations not finished!')   
    
    # Check record counts
    check_round1_relax(static_df, ref_df, evsr_df)

    ########################### Load dynamic1 records ##########################
    if all_dynamic_df is None:
        dynamic1_df = database.get_records_df(style='calculation_relax_dynamic',
                                              branch='main',
                                              potential_key=potential_key,
                                              potential_LAMMPS_key=potential_LAMMPS_key)
    else:
        ix = (
            (all_dynamic_df.branch == 'main') &
            (all_dynamic_df.potential_key == potential_key) &
            (all_dynamic_df.potential_LAMMPS_key == potential_LAMMPS_key))
        dynamic1_df = all_dynamic_df[ix].reset_index(drop=True)        
    
    if verbose:
        print(len(dynamic1_df), 'relax_dynamic:main calculations found')
    
    if sum(dynamic1_df.status == 'not calculated') > 0:
        raise ValueError('Some relax_dynamic calculations not finished!')   
    
    # Check record counts
    check_round1_relax(dynamic1_df, ref_df, evsr_df)

    ########################### Load dynamic2 records ##########################
    if all_static_df is None:
        dynamic2_df = database.get_records_df(style='calculation_relax_static',
                                              branch='from_dynamic',
                                              potential_key=potential_key,
                                              potential_LAMMPS_key=potential_LAMMPS_key)
    else:
        ix = (
            (all_static_df.branch == 'from_dynamic') &
            (all_static_df.potential_key == potential_key) &
            (all_static_df.potential_LAMMPS_key == potential_LAMMPS_key))
        dynamic2_df = all_static_df[ix].reset_index(drop=True)
    
    if verbose:
        print(len(dynamic2_df), 'relax_static:from_dynamic calculations found')

    if sum(dynamic2_df.status == 'not calculated') > 0:
        raise ValueError('Some relax_static:from_dynamic calculations not finished!')   
    
    # Check record counts
    check_round2_relax(dynamic1_df, dynamic2_df)

    ############################ Combine relax records #########################
    box_df['method'] = 'box'
    static_df['method'] = 'static'
    dynamic2_df['method'] = 'dynamic'
    relax_df = pd.concat([box_df, static_df, dynamic2_df],
                         ignore_index=True, sort=False)

    return relax_df
    
def check_round1_relax(df: pd.DataFrame,
                       ref_df: pd.DataFrame,
                       evsr_df: pd.DataFrame):
    """
    Check the counts of first round relaxation calculations

    Parameters
    ----------
    df : pandas.DataFrame
        The first round relaxation records to check
    ref_df : pandas.DataFrame
        The reference crystals with corresponding elements/symbols
    evsr_df : pandas.DataFrame
        The E_vs_r_scan records for the potential
    """

    # Check all records have identified parents
    no_parents = df[~df.parent_key.isin(ref_df.id.tolist() + evsr_df.key.tolist())]
    if len(no_parents) > 0:
        print('Calculations without parents found!')
        print(no_parents.key.tolist())

    # Check that all refs have exactly one calc
    bad = False
    for i in ref_df.index:
        ref_series = ref_df.loc[i]
        siblings = df[df.parent_key == ref_series.id]
        if len(siblings) == 0:
            print('Missing calculation for', ref_series.id)
            bad = True
        elif len(siblings) > 1:
            print('Extra (duplicate?) calculations found:')
            print(siblings.key.tolist())

    # Check for correct number of min cells to calcs
    for i in evsr_df.index:
        evsr_series = evsr_df.loc[i]
        siblings = df[df.parent_key == evsr_series.key]
        if len(siblings) < evsr_series.num_min_cells:
            print('Missing calculation for', evsr_series.key)
            bad = True
        elif len(siblings) > evsr_series.num_min_cells:
            print('Extra (duplicate?) calculations found:')
            print(siblings.key.tolist())

    if bad:
        raise ValueError('Missing calculations')
            
def check_round2_relax(dynamic1_df: pd.DataFrame,
                       dynamic2_df: pd.DataFrame):
    """
    Check the counts of second round relaxation calculations.

    Parameters
    ----------
    dynamic1_df : pandas.DataFrame
        The metadata for round 1 dynamic relaxations (relax_dynamic:main).
    dynamic2_df : pandas.DataFrame 
        The metadata for round 2 dynamic relaxations (relax_static:from_dynamic).
    """
    round2_parent_keys = dynamic1_df[dynamic1_df.status=='finished'].key.tolist()
    
    bad = False
    for round2_parent_key in round2_parent_keys:
        siblings = dynamic2_df[dynamic2_df.parent_key == round2_parent_key]
        if len(siblings) == 0:
            print('Missing calculation for', round2_parent_key)
            bad = True
        elif len(siblings) > 1:
            print('Extra (duplicate?) calculations found:')
            print(siblings.key.tolist())
    if bad:
        raise ValueError('Missing calculations')
            
def merge_spg_info(database: IprPyDatabase,
                   relax_df: pd.DataFrame,
                   all_spg_df: Optional[pd.DataFrame] = None,
                   verbose: bool = False
                   ) -> pd.DataFrame:
    """
    Merges relaxation metadata with the corresponding crystal space group
    metadata.  Checks the status and count of the crystal_space_group
    calculations generated from the relax results.

    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    relax_df : pandas.DataFrame
        The combined metadata for all relax calculations.  Use
        get_relax_df() to build this.
    all_spg_df : pandas.DataFrame, optional
        The metadata for all crystal_space_group calculation records.  If not
        given, a fresh query to the database will be performed.
    
    Raises
    ------
    ValueError
        If any of the crystal_space_group calculations for the potential have a
        status of "not calculated".
    
    Returns
    -------
    relax_df: pandas.DataFrame
        The original relax_df with space group metadata added in and trimmed to
        exclude calculation error results.
    """

    return_keys = ['key', 'parent_key', 'family', 'symbols', 'composition',
            'potential_LAMMPS_key', 'potential_LAMMPS_id', 'potential_key', 'potential_id',
            'method', 'a', 'b', 'c', 'alpha', 'beta', 'gamma', 'E_pot',
            'spacegroup_number', 'pearson_symbol']
    sort_keys = ['composition', 'E_pot']
    
    if all_spg_df is None:
        all_spg_df = database.get_records_df(style='calculation_crystal_space_group',
                                             branch='relax')

    # Find spg results for relax calculations
    spg_df = all_spg_df[all_spg_df.parent_key.isin(relax_df.key)]

    if verbose:
        print(len(spg_df), 'crystal_space_group calculations found')

    if sum(spg_df.status == 'not calculated') > 0:
        raise ValueError('Some crystal_space_group calculations not finished!')    
    
    # Check that all relaxes have exactly one spg
    bad = False
    for i in relax_df[relax_df.status=='finished'].index:
        relax_series = relax_df.loc[i]
        siblings = spg_df[spg_df.parent_key == relax_series.key]
        if len(siblings) == 0:
            print('Missing calculation for', relax_series.key)
            bad = True
        elif len(siblings) > 1:
            print('Extra (duplicate?) calculations found:')
            print(siblings.key.tolist())
    
    if bad:
        raise ValueError('Missing calculations')
    
    merged_df = pd.merge(spg_df, relax_df[relax_df.status=='finished'],
                         left_on='parent_key', right_on='key',
                         suffixes=('', '_parent'), validate='one_to_one')
    
    merged_df = merged_df[merged_df.status == 'finished'][return_keys].sort_values(sort_keys).reset_index(drop=True)

    if verbose:
        print(len(merged_df), 'combined relax + space group results compiled')

    return merged_df
    
def identify_transformed(database: IprPyDatabase,
                         relax_df: pd.DataFrame,
                         all_spg_df: Optional[pd.DataFrame] = None):
    """
    Compares space group information of the relaxed crystals to the
    corresponding information calculated for the original family structure.
    Adds a "transformed" field to the relax_df dataframe.

    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    relax_df : pandas.DataFrame
        The combined metadata for all relax calculations plus associated space
        group information.  Use get_relax_df() and merge_spg_info() to build
        this.
    all_spg_df : pandas.DataFrame, optional
        The metadata for all crystal_space_group calculation records.  If not
        given, a fresh query to the database will be performed.
    """
    # Get space group details for the original prototype/reference structures
    if all_spg_df is None:
        source_spg_df = database.get_records_df(style='calculation_crystal_space_group',
                                                branch=['prototype', 'reference'])
    else:
        source_spg_df = all_spg_df[all_spg_df.branch.isin(['prototype', 'reference'])]
    
    def get_transformed(series, source_spg_df):
        """
        Identify transformed structures by comparing space group info before/after relax
        """
        # Fetch the matching source record
        matches = source_spg_df[source_spg_df.family == series.family]
        try:
            source_series = matches.iloc[0]
        except:
            return np.nan

        # Identify if transformed based on spacegroup and Pearson symbol
        return (not (source_series.spacegroup_number == series.spacegroup_number
                    and source_series.pearson_symbol == series.pearson_symbol))

    # Apply get_transformed to relax_df
    relax_df['transformed'] = relax_df.apply(get_transformed, axis=1,
                                             args=[source_spg_df])

    return relax_df

def identify_prototype(database: IprPyDatabase,
                       relax_df: pd.DataFrame,
                       ref_proto_df: Optional[pd.DataFrame] = None,
                       all_spg_df: Optional[pd.DataFrame] = None):
    """
    Adds the "prototype" field to the relax_df based on if the family is a
    reference crystal that matches with a crystal prototype.

    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    relax_df : pandas.DataFrame
        The combined metadata for all relax calculations plus associated space
        group information.  Use get_relax_df() and merge_spg_info() to build
        this.
    ref_proto_df : pandas.DataFrame, optional
        A table linking reference crystal structures to known crystal
        prototypes.  If not given, match_reference_prototype() will be called.
    all_spg_df : pandas.DataFrame, optional
        The metadata for all crystal_space_group calculation records.  If not
        given and ref_proto_df is not given, a fresh query to the database will
        be performed.
    """
    if ref_proto_df is None:
        ref_proto_df = match_reference_prototype(database, all_spg_df=all_spg_df)
    
    # Set prototype as prototype if given or family if not
    def get_prototype(series, ref_proto_df):
        # Match relax family to ref in ref_proto_df
        matches = ref_proto_df[ref_proto_df.reference == series.family]
        try:
            # Check if a match exists and has an associated prototype 
            ref_proto_series = matches.iloc[0]
            assert not pd.isnull(ref_proto_series.prototype)
        except:
            # Return relax family as default
            return series.family
        else:
            # Return ref's prototype if known
            return ref_proto_series.prototype
    
    # Apply get_prototype to relax_df
    relax_df['prototype'] = relax_df.apply(get_prototype, axis=1,
                                           args=[ref_proto_df])
    
    return relax_df

def trim_ucell(ucell: am.System,
               atom_style: str = 'atomic'):
    """
    Fix to remove extra per-atom fields from the ucell

    Parameters
    ----------
    ucell : atomman.System
        The unit cell system identified by a crystal_space_group calculation
    potential : potentials.record.BasePotentialLAMMPS.BasePotentialLAMMPS
        The potential_LAMMPS record associated with the unit cell.
    """
    ucell = deepcopy(ucell)
    
    keys = list(ucell.atoms.view)
    for key in keys:
        if key in ['atype', 'pos']:
            continue
        elif key == 'charge' and atom_style == 'charge':
            continue
        del ucell.atoms.view[key]
    
    return ucell

def calculate_cohesive_energy(series, ucell, iso_energy_df):
    """
    Compute the cohesive energy for a unit cell based on 
    """
    # Compute base_energy
    atypes, counts = np.unique(ucell.atoms.atype, return_counts=True)
    base_energy = 0
    for symbol, count in zip(ucell.symbols, counts):
        E = iso_energy_df[(iso_energy_df.potential_LAMMPS_key == series.potential_LAMMPS_key) &
                          (iso_energy_df.symbol == symbol)].isolated_atom_energy.values[0]
        base_energy += E * count
    base_energy = base_energy / ucell.natoms
    
    return series.E_pot - base_energy

def build_relaxed_crystal(series: pd.Series,
                          ucell: am.System,
                          E_coh: Optional[float] = None,
                          standing: str = 'good'):
    """
    Builds a new relaxed_crystal record.

    Parameters
    ----------
    series : pd.Series
        A data series associated with combined relax and space group info.
    ucell : am.System
        The space group unit cell system associated with series.
    E_coh : float, optional
        The per-atom cohesive energy for ucell.  If not given, E_coh will be
        set to series.E_pot.
    standing : str, optional
        The standing state to assign to the relaxed_crystal.  Default value is
        "good".
    """
    def handle_symbols(series):
        symbols = series.symbols.split()
        if len(symbols) == 1:
            return symbols[0]
        return symbols
    
    model = DM()
    model['relaxed-crystal'] = crystal = DM()
    
    crystal['key'] = str(uuid4())
    crystal['method'] = series.method
    crystal['standing'] = standing
    
    crystal['potential-LAMMPS'] = DM()
    crystal['potential-LAMMPS']['key'] = series.potential_LAMMPS_key
    crystal['potential-LAMMPS']['id'] = series.potential_LAMMPS_id
    crystal['potential-LAMMPS']['potential'] = DM()
    crystal['potential-LAMMPS']['potential']['key'] = series.potential_key
    crystal['potential-LAMMPS']['potential']['id'] = series.potential_id
    
    crystal['system-info'] = DM()
    crystal['system-info']['family'] = series.family
    crystal['system-info']['parent_key'] = series.key
    crystal['system-info']['symbol'] = handle_symbols(series)
    crystal['system-info']['composition'] = series.composition
    crystal['system-info']['cell'] = DM()
    crystal['system-info']['cell']['crystal-family'] = ucell.box.identifyfamily()
    crystal['system-info']['cell']['natypes'] = ucell.natypes
    crystal['system-info']['cell']['a'] = series.a
    crystal['system-info']['cell']['b'] = series.b
    crystal['system-info']['cell']['c'] = series.c
    crystal['system-info']['cell']['alpha'] = series.alpha
    crystal['system-info']['cell']['beta'] = series.beta
    crystal['system-info']['cell']['gamma'] = series.gamma
    
    crystal['atomic-system'] = ucell.model(box_unit='angstrom')['atomic-system']
    
    crystal['potential-energy'] = uc.model(series.E_pot, 'eV')
    
    if E_coh is None:
        crystal['cohesive-energy'] = uc.model(series.E_pot, 'eV')
    else:
        crystal['cohesive-energy'] = uc.model(E_coh, 'eV')
    
    return model

def create_missing_relaxed_crystals(database: IprPyDatabase,
                                    relax_df: pd.DataFrame,
                                    potential_LAMMPS_key: str,
                                    potential_key: str,
                                    atom_style: str = 'atomic',
                                    iso_energy_df: Optional[pd.DataFrame] = None,
                                    verbose: bool = False):
    
    # Get iso_energy_df if needed
    if iso_energy_df is None:
        iso_energy_df = get_isolated_atom_energies(database)

    # Filter out transformed
    relax_df = relax_df[relax_df.transformed==False]

    if verbose:
        print(len(relax_df), 'did not transform')

    # Get existing relaxed_crystal records
    crystals_df = database.get_records_df(style='relaxed_crystal', 
                                          potential_LAMMPS_key=potential_LAMMPS_key,
                                          potential_key=potential_key)
    if verbose:
        print(len(crystals_df), 'relaxed_crystal records found')
    if len(crystals_df) == 0:
        crystals_df = pd.DataFrame(columns=['parent_key'])

    # Check for missing parents
    no_parents = crystals_df[~crystals_df.parent_key.isin(relax_df.key)]
    if len(no_parents) > 0:
        print('Calculations without parents found!')
        print(no_parents.key.tolist())

    # Check for missing relaxed_crystals
    missing_df = relax_df[~relax_df.key.isin(crystals_df.parent_key)].reset_index(drop=True)
    if verbose:
        print(len(missing_df), 'relaxed_crystal records to create')

    # Fetch crystal_space_group for the missing crystals (necessary for ucell)
    spg_records = database.get_records('calculation_crystal_space_group', key=missing_df.key.tolist()) 

    for i in range(len(spg_records)):
        
        # Get a single record and the matching collected data
        spg_record = spg_records[i]
        series = missing_df[missing_df.key == spg_record.key].iloc[0]

        # Trim ucell
        ucell = trim_ucell(spg_record.spg_ucell, atom_style)

        # Calculate E_coh
        E_coh = calculate_cohesive_energy(series, ucell, iso_energy_df)

        # Build and add record to database
        model = build_relaxed_crystal(series, ucell, E_coh=E_coh)
        record = RelaxedCrystal(model=model)
        database.add_record(record=record, verbose=verbose)

def identify_duplicates(database: IprPyDatabase,
                        potential_LAMMPS_key: str,
                        potential_key: str,
                        verbose: bool = False):
    """
    Compares E_coh and lattice constants of all relaxed_crystal records still
    with standing='good' to identify duplicates and change their standing to
    'bad'.
    
    Parameters
    ----------
    database : iprPy.database.IprPyDatabase
        The database to access (if needed).
    potential_LAMMPS_key : str
        The UUID4 associated with the potential implementation.
    potential_LAMMPS_id : str
        The UUID4 associated with the potential model.
    """
    
    # Get relaxed_crystal records
    crystals, crystals_df = database.get_records(style='relaxed_crystal', return_df=True, 
                                                 potential_LAMMPS_key=potential_LAMMPS_key,
                                                 potential_key=potential_key)
    
    if verbose:
        print(len(crystals), 'relaxed_crystal records found')
    if len(crystals) == 0:
        return

    # Add parent_type for sorting
    def set_parent_type(series):
        if series.family[0] == 'm' or series.family[0] == 'o':
            return 'reference'
        else:
            return 'prototype'
    crystals_df['parent_type'] = crystals_df.apply(set_parent_type, axis=1)

    # Add method_int for sorting
    def set_method_int(series):
        if series.method == 'dynamic':
            return 1
        elif series.method == 'static':
            return 2
        else:
            return 3
    crystals_df['method_int'] = crystals_df.apply(set_method_int, axis=1)
    
    # Limit to current records with "good" standing
    good_df = crystals_df[crystals_df.standing == 'good']
    if verbose:
        print(f' - {len(good_df)} currently have good standing')
     
    # Iterate over each unique composition for a potential implementation
    for composition in np.unique(good_df.composition):
        composition_df = good_df[good_df.composition == composition]
        skips = []

        # Iterate over records sorted by relaxation method and prototype vs. reference
        for i in composition_df.sort_values(['method_int', 'parent_type']).index:

            # Skip if record's standing has been changed
            if crystals[i].standing == 'bad':
                continue

            # Add current entry to skips (so later records ignore it)
            skips.append(i)

            # Count number of matching records
            series = crystals_df.loc[i]
            matches = (np.isclose(series.cohesive_energy, composition_df.cohesive_energy)
                      &np.isclose(series.a, composition_df.a)
                      &np.isclose(series.b, composition_df.b)
                      &np.isclose(series.c, composition_df.c)
                      &np.isclose(series.alpha, composition_df.alpha)
                      &np.isclose(series.beta, composition_df.beta)
                      &np.isclose(series.gamma, composition_df.gamma))

            if np.sum(matches) > 1:
                for j in composition_df[matches].index:
                    if j not in skips:
                        record = crystals[j]
                        record.model['relaxed-crystal']['standing'] = 'bad'
                        database.update_record(record=record, verbose=verbose)
                        skips.append(j)
    
    # Reload relaxed_crystal records from the database
    crystals = database.get_records(style='relaxed_crystal', standing='good',
                                    potential_LAMMPS_key=potential_LAMMPS_key,
                                    potential_key=potential_key)
    
    print(f' - {len(crystals)} retain good standing')
