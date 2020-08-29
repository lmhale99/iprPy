import uuid

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc
import atomman.lammps as lmp
import atomman as am

# https://pandas.pydata.org/
import pandas as pd

from ... import load_database, load_record

def relaxed(database_name, crystal_match_file, all_crystals_file,
            unique_crystals_file):
    """
    Processes crystal relaxation results to generate relaxed_crystal records
    and filter out duplicates.
    
    Parameters
    ----------
    database_name : str
        The name of the database to access.
    crystal_match_file : str
        The file path for the csv file containing the identified
        reference-prototype matches.
    all_crystals_file : str
        The file path for the csv file where the compiled results are to be
        saved to.
    unique_crystals_file : str
        The file path for the csv file where the compiled results for only the
        unique crystals are saved to.
    """
    results = compile_relaxation_results(database_name, crystal_match_file,
                                         all_crystals_file)
                               
    create_relaxed_crystal_records(database_name, results=results)
    
    identify_duplicates(database_name, unique_crystals_file, results=results)

def save_keys():
    """The list of keys to include in the all and unique results csv files"""
    return ['calc_key', 'potential_LAMMPS_key', 'potential_LAMMPS_id', 'potential_key',
            'potential_id', 'composition', 'prototype', 'family', 'parent_key', 'method',
            'transformed', 'E_coh', 'a', 'b', 'c', 'alpha', 'beta', 'gamma']

def results_keys():
    """
    The list of keys to include in the results dataframe
    """
    return save_keys() + ['ucell', 'ucell_family']

def sort_keys():
    """The list of keys to sort by for the all and unique results csv files"""
    return ['potential_LAMMPS_id', 'composition', 'prototype', 'family', 'E_coh']

def compile_relaxation_results(database_name, crystal_match_file,
                               all_crystals_file):
    """
    Compiles results of calculation_relax_box, calculation_relax_static, and
    calculation_crystal_space_group records.
    
    Parameters
    ----------
    database_name : str
        The name of the database to access.
    crystal_match_file : str
        The file path for the csv file containing the identified
        reference-prototype matches.
    all_crystals_file : str
        The file path for the csv file where the compiled results are to be
        saved to.
        
    Returns
    -------
    pandas.DataFrame
        The compiled results
        
    Raises
    ------
    ValueError
        If no calculation_crystal_space_group records found for relaxations
        and/or reference+prototype structures.
    """
    
    # Access the database
    database = load_database(database_name)

    # Load relax_box records
    raw_df = database.get_records_df(style='calculation_relax_box',
                                    full=True, flat=True)
    print(f'{len(raw_df)} calculation_relax_box records found', flush=True)

    if len(raw_df) > 0:
        # Take branch='main' and assign method='box'
        box_df = raw_df[raw_df.branch=='main'].reset_index(drop=True)
        box_df['method'] = 'box'
        print(f" - {len(box_df)} are branch main", flush=True)
    
    else:
        # Create empty DataFrame if no calculation_relax_box records found
        box_df = pd.DataFrame()

    # Load relax_static records
    raw_df = database.get_records_df(style='calculation_relax_static',
                                    full=True, flat=True)
    print(f'{len(raw_df)} calculation_relax_static records found', flush=True)

    if len(raw_df) > 0:
        # Take branch='main' and assign method='static'
        static_df = raw_df[raw_df.branch=='main'].reset_index(drop=True)
        static_df['method'] = 'static'
        print(f" - {len(static_df)} are branch main", flush=True)
        
        # Take branch='from_dynamic' and assign method='dynamic'
        dynamic_df = raw_df[raw_df.branch=='from_dynamic'].reset_index(drop=True)
        dynamic_df['method'] = 'dynamic'
        print(f" - {len(dynamic_df)} are branch from_dynamic", flush=True)
    
    else:
        # Create empty DataFrames if no calculation_relax_static records found
        static_df = pd.DataFrame()
        dynamic_df = pd.DataFrame()

    # Merge all relax entries into a single dataframe
    parent_df = pd.concat([box_df, static_df, dynamic_df], ignore_index=True, sort=False)

    # Load space group results
    spg_records = database.get_records_df(style='calculation_crystal_space_group',
                                        full=True, flat=False, status='finished')
    print(f'{len(spg_records)} calculation_crystal_space_group records found',
        flush=True)

    if len(spg_records) > 0:
        # Separate out records with branch='prototype' or 'reference'
        family_records = spg_records[(spg_records.branch == 'prototype') 
                                    |(spg_records.branch == 'reference')]
        print(f' - {len(family_records[family_records.branch == "prototype"])} are for prototypes', flush=True)
        print(f' - {len(family_records[family_records.branch == "reference"])} are for references', flush=True)
        if len(family_records) == 0:
            raise ValueError('No calculation_crystal_space_group records for prototypes/references found')
        
        # Separate out records with branch='relax'
        calc_records = spg_records[spg_records.branch == 'relax'].reset_index(drop=True)
        print(f' - {len(calc_records)} are for calculations', flush=True)
        if len(calc_records) == 0:
            raise ValueError('No calculation_crystal_space_group records for relaxations found')
    else:
        raise ValueError('No calculation_crystal_space_group records found')
    
    # Load crystal_match_file
    try:
        ref_proto_match = pd.read_csv(crystal_match_file)
    except:
        columns = ['reference', 'prototype', 'composition']
        ref_proto_match = pd.DataFrame(columns=columns)
    print(f'{len(ref_proto_match)} references matched to prototypes', flush=True)

    # Get parent keys (relax_*) for calculation_crystal_space_group records
    def get_parent(series):
        return series.load_file.split('/')[0]
    calc_records['parent'] = calc_records.apply(get_parent, axis=1)

    # Merge calc_records, family_records and ref_proto_match
    merged_df = pd.merge(
                    pd.merge(
                        pd.merge(calc_records, parent_df, left_on='parent', right_on='key', suffixes=('', '_parent'), validate='one_to_one'),
                        family_records, on='family', suffixes=('', '_family'), validate="many_to_one"),
                    ref_proto_match, how='left', left_on='family', right_on='reference', suffixes=('', '_ref'))

    # Direct copy values from merged_df to results
    results = {}
    results['calc_key'] = merged_df.key
    results['potential_LAMMPS_key'] = merged_df.potential_LAMMPS_key
    results['potential_LAMMPS_id'] = merged_df.potential_LAMMPS_id
    results['potential_key'] = merged_df.potential_key
    results['potential_id'] = merged_df.potential_id
    results['composition'] = merged_df.composition
    results['family'] = merged_df.family
    results['method'] = merged_df.method
    results['parent_key'] = merged_df.parent
    results['E_coh'] = merged_df.E_cohesive
    results['prototype'] = merged_df.prototype
    results['ucell'] = merged_df.ucell
    results['ucell_family'] = merged_df.ucell_family

    # Identify transformed structures by comparing space group info before/after relax
    def get_transformed(series):
        return (not (series.spacegroup_number_family == series.spacegroup_number
                    and series.pearson_symbol_family == series.pearson_symbol))
    results['transformed'] = merged_df.apply(get_transformed, axis=1)

    # Set prototype as prototype if given or family if not
    def get_prototype(series):
        # Identify prototype
        if pd.isnull(series.prototype):
            return series.family
        else:
            return series.prototype
    results['prototype'] = merged_df.apply(get_prototype, axis=1)

    # Extract lattice constants from ucell
    def get_a(series):
        return series.ucell.box.a
    def get_b(series):
        return series.ucell.box.b
    def get_c(series):
        return series.ucell.box.c
    def get_alpha(series):
        return series.ucell.box.alpha
    def get_beta(series):
        return series.ucell.box.beta
    def get_gamma(series):
        return series.ucell.box.gamma
    results['a'] = merged_df.apply(get_a, axis=1)
    results['b'] = merged_df.apply(get_b, axis=1)
    results['c'] = merged_df.apply(get_c, axis=1)
    results['alpha'] = merged_df.apply(get_alpha, axis=1)
    results['beta'] = merged_df.apply(get_beta, axis=1)
    results['gamma'] = merged_df.apply(get_gamma, axis=1)

    # Create results DataFrame and save to all_crystals_file
    results = pd.DataFrame(results, columns=results_keys()).sort_values(sort_keys())
    results[save_keys()].to_csv(all_crystals_file, index=False)
    print(all_crystals_file, 'updated')

    return results

def create_relaxed_crystal_records(database_name, results=None, all_crystals_file=None):
    """
    Generates new relaxed_crystal records based on the untransformed listings
    from the compiled relaxation results.
    
    Parameters
    ----------
    database_name : str
        The name of the database to access.
    results : pandas.DataFrame, optional
        The compiled relaxation results.  Either but not both of results and
        all_crystals_file must be given.
    all_crystals_file : str, optional
        The file path to the csv file where the compiled relaxation results
        are saved.  Either but not both of results and all_crystals_file must
        be given.
    
    """
    # Access the database
    database = load_database(database_name)
    
    # Load results from all_crystals_file if needed
    if results is None:
        if all_crystals_file is not None:
            results = pd.read_csv(all_crystals_file)
        else:
            raise TypeError('results or all_crystals_file must be given')
    elif all_crystals_file is not None:
        raise TypeError('results and all_crystals_file cannot both be given')
    
    # Filter out the transformed results
    results = results[~results.transformed]
    print(len(results), 'untransformed crystals found in the compiled relaxation results')
   
    # Load existing relaxed_crystal records from the database 
    relaxed_records = database.get_records_df(style='relaxed_crystal', full=True, flat=False)
    print(len(relaxed_records), 'relaxed_crystal records found in the database')

    # Identify new results using parent_key (i.e. one relaxed_crystal per parent)
    newresults = results[~results.calc_key.isin(relaxed_records.parent_key)]
    print(f' - {len(newresults)} new results to add')

    # Load potential_LAMMPS records
    potential_records, potential_records_df = database.get_records(style='potential_LAMMPS', return_df=True)

    # Loop over all new records
    for i in newresults.index:
        series = newresults.loc[i]
                
        # Create new record
        key = str(uuid.uuid4())
        record = load_record('relaxed_crystal', name=key)
        
        # Set simple properties
        input_dict = {}
        input_dict['key'] = key
        input_dict['method'] = series.method
        input_dict['family'] = series.family
        input_dict['parent_key'] = series.calc_key
        input_dict['length_unit'] = 'angstrom'
        input_dict['energy_unit'] = 'eV'
        input_dict['E_coh'] = series.E_coh
        
        # Set potential
        try:
            potential_record = potential_records[potential_records_df[potential_records_df.key == series.potential_LAMMPS_key].index[0]]
        except:
            print(f'potential {series.potential_LAMMPS_id}({series.potential_LAMMPS_key}) not found for calculation {series.calc_key}')
            continue
        input_dict['potential'] = lmp.Potential(potential_record.content)
        
        # Set ucell
        # Use spg crystals for ref and α-As
        if (series.prototype[:3] == 'mp-' or
            series.prototype[:4] == 'mvc-' or
            series.prototype[:5] == 'oqmd-' or
            series.prototype == 'A7--alpha-As'):
            ucell = series.ucell

        # Use scaled prototype crystals for the rest
        else:
            ucell = series.ucell_family
            ucell.symbols = series.ucell.symbols
            ucell.box_set(vects=series.ucell.box.vects, scale=True)
        input_dict['ucell'] = ucell
        
        # Set standing as bad for structures with positive or near-zero energies
        if series.E_coh < -1e-5:
            input_dict['standing'] = 'good'
        else:
            input_dict['standing'] = 'bad'
        
        # Build content and upload
        record.buildcontent(input_dict)
        database.add_record(record=record)

def identify_duplicates(database_name, unique_crystals_file, results=None,
                        all_crystals_file=None):
    """
    Compares E_coh and lattice constants of all relaxed_crystal records still
    with standing='good' to identify duplicates and change their standing to
    'bad'.
    
    Parameters
    ----------
    database_name : str
        The name of the database to access.
    unique_crystals_file : str
        The file path for the csv file where the compiled results for only the
        unique crystals are saved to.
    results : pandas.DataFrame, optional
        The compiled relaxation results.  Either but not both of results and
        all_crystals_file must be given.
    all_crystals_file : str, optional
        The file path to the csv file where the compiled relaxation results
        are saved.  Either but not both of results and all_crystals_file must
        be given.
    """
    # Access the database
    database = load_database(database_name)
    
    # Load results from all_crystals_file if needed
    if results is None:
        if all_crystals_file is not None:
            results = pd.read_csv(all_crystals_file)
        else:
            raise TypeError('results or all_crystals_file must be given')
    elif all_crystals_file is not None:
        raise TypeError('results and all_crystals_file cannot both be given')
    
    # Filter out the transformed results
    results = results[~results.transformed]
    
    # Load relaxed_crystal records from the database
    records, records_df = database.get_records(style='relaxed_crystal', return_df=True)
    print(len(records), 'relaxed records found')
    print(f' - {len(records_df[records_df.standing=="good"])} currently have good standing')

    # Add parent_type and method_int keys to records_df for sorting by importance
    def set_parent_type(series):
        if series.family[0] == 'm' or series.family[0] == 'o':
            return 'reference'
        else:
            return 'prototype'
    records_df['parent_type'] = records_df.apply(set_parent_type, axis=1)

    def set_method_int(series):
        if series.method == 'dynamic':
            return 1
        elif series.method == 'static':
            return 2
        else:
            return 3
    records_df['method_int'] = records_df.apply(set_method_int, axis=1)
    
    # Iterate over each unique potential implementation
    good_df = records_df[records_df.standing == 'good']
    for potential_LAMMPS_key in np.unique(good_df.potential_LAMMPS_key):
        potential_df = good_df[good_df.potential_LAMMPS_key == potential_LAMMPS_key]
        
        # Iterate over each unique composition for a potential implementation
        for composition in np.unique(potential_df.composition):
            composition_df = potential_df[potential_df.composition == composition]
            skips = []
            
            # Iterate over records sorted by relaxation method and prototype vs. reference
            for i in composition_df.sort_values(['method_int', 'parent_type']).index:
                
                # Skip if record's standing has been changed
                if records[i].content['relaxed-crystal']['standing'] == 'bad':
                    continue
                
                # Add current entry to skips (so later records ignore it)
                skips.append(i)
                
                # Count number of matching records
                series = records_df.loc[i]
                matches = (np.isclose(series.E_coh, composition_df.E_coh)
                          &np.isclose(series.a, composition_df.a)
                          &np.isclose(series.b, composition_df.b)
                          &np.isclose(series.c, composition_df.c)
                          &np.isclose(series.alpha, composition_df.alpha)
                          &np.isclose(series.beta, composition_df.beta)
                          &np.isclose(series.gamma, composition_df.gamma))
                
                if np.sum(matches) > 1:
                    for j in composition_df[matches].index:
                        if j not in skips:
                            record = records[j]
                            record.content['relaxed-crystal']['standing'] = 'bad'
                            database.update_record(record=record)
                            skips.append(j)
    
    # Reload relaxed_crystal records from the database
    relaxed_records = database.get_records_df(style='relaxed_crystal', full=True, flat=False)
    print(f' - {len(relaxed_records[relaxed_records.standing=="good"])} retain good standing')

    unique_results = pd.merge(results, relaxed_records, left_on='calc_key', right_on='parent_key', suffixes=('', '_dup'), validate='one_to_one')
    unique_results = unique_results[unique_results.standing=='good'].sort_values(sort_keys())

    unique_results[save_keys()].to_csv(unique_crystals_file, index=False)
    print(unique_crystals_file, 'updated')
