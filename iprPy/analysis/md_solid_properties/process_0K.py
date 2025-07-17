from typing import Union

from copy import deepcopy
from uuid import uuid4



from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc



import numpy as np

import pandas as pd

from tqdm import tqdm



def process_0K(database,
               potential_LAMMPS_id: Union[str, list, None] = None,
               strainrange: float = 1e-7,
               verbose: bool = False):
    """
    Constructs md_solid_properties records by combining relaxed_crystal records
    with elastic_constants_static results.

    Notes: This relies on relaxed_crystal records, so it should be called after
    they are built with the process_relaxations() method.  The records built
    by this method collect the static results so that they can be easily
    plotted alongside the at temperature structure results.

    Properties
    ----------
    database : iprPy.Database
        The database to interact with where existing records are to be found
        and new md_solid_properties will be added to.
    potential_LAMMPS_id : str, list or None, optional
        One or more potential_LAMMPS_ids that will limit the records being
        queried, parsed and built to only those associated with the indicated
        potentials.  If None, then all potentials will be explored which can
        take some time and require large amounts of memory.
    strainrange : float, optional
        The strainrange value of the elastic_constants_static results to use.
        The default iprPy workflow performs the elastic_constants_static
        calculation with different strainranges to search for sensitivities.
        The default value is 1e-7, which is likely good for most potentials
        and crystals.
    verbose : bool, optional
        Informative messages will be printed if verbose is set to True.
    
    Returns
    -------
    count_add : int
        The number of new records added.
    count_update : int
        The number of old records updated with Cij results.
    """

    # Fetch existing md_solid_properties results
    results, results_df = database.get_records('md_solid_properties', return_df=True,
                                               potential_LAMMPS_id=potential_LAMMPS_id,
                                               method='0K')
    if verbose:
        print(len(results), 'md_solid_properties:0K records found', flush=True)
    
    # Create empty dataframe if needed
    if len(results) == 0:
        keys = ['potential_LAMMPS_key', 'potential_key', 'relaxed_crystal_key', 'method']
        results_df = pd.DataFrame(columns=keys)

    # Fetch good, dynamic relaxed relax_crystal records
    crystals, crystals_df = database.get_records('relaxed_crystal', return_df=True,
                                                 standing='good', method='dynamic',
                                                 potential_LAMMPS_id=potential_LAMMPS_id)
    if verbose:
        print(len(crystals), 'relaxed_crystal records found', flush=True)

    # Fetch finished elastic_constants_static results
    cijs, cijs_df = database.get_records('calculation_elastic_constants_static', return_df=True,
                                         status='finished',
                                         potential_LAMMPS_id=potential_LAMMPS_id,
                                         strainrange=strainrange)
    if verbose:
        print(len(cijs), 'elastic_constants_static records found', flush=True)

    

    count_add = 0
    count_update = 0
    for crystal in crystals:
        updated = False
        
        # Search for existing record
        match = results_df[
            #(results_df.potential_LAMMPS_key == crystal.potential_LAMMPS_key) &
            #(results_df.potential_key == crystal.potential_key) &
            (results_df.method == '0K') &
            (results_df.relaxed_crystal_key == crystal.key)]
        
        if len(match) == 0:
            # Create a new solid results record and add crystal info
            solid = am.library.load_record('md_solid_properties')
            solid.new_name()
            solid.extract_relaxed_crystal(crystal)
            updated = True
        
        elif len(match) == 1:
            # Get the existing record
            solid = results[match.index[0]]
        
        else:
            raise ValueError('Multiple solid records!!!')

        # Add Cij results if not already in the record and they exist
        if solid.C is None:
            match = cijs_df[cijs_df.parent_key == crystal.key]
            
            if len(match) == 1:
                cij = cijs[match.index[0]]
                solid.extract_elastic_constants(cij)
                updated = True
            elif len(match) > 1:
                raise ValueError('Multiple elastic constants records!!!')
        
        if updated:
            solid.build_model()
            try:
                database.add_record(solid)
                count_add += 1
            except:
                database.update_record(solid)
                count_update += 1
            
    if verbose:
        print(count_add, 'records added')
        print(count_update, 'records updated')

    return count_add, count_update