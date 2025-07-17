from typing import Union

from copy import deepcopy
from uuid import uuid4



from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc



import numpy as np

import pandas as pd

from tqdm import tqdm



def process_at_temp(database,
                    potential_LAMMPS_id: Union[str, list, None] = None,
                    verbose: bool = False):
    """
    Constructs md_solid_properties records by combining finished 
    relax_dynamic:at_temp(_50K), elastic_constants_dynamic and free_energy
    calculation results.

    Notes: This method assumes that the standard iprPy workflow was used to
    generate the associated calculations.  As such, it may not work otherwise.

    Expected workflow:
    1. relaxed_crystal records built from static results using
       process_relaxations().
    2. md_solid_properties records built from the relaxed_crystal records using
       process_md_solid_properties_0K().
    3. relax_dynamic:at_temp_50K calculations ran that use relaxed_crystal records
       as their parent structures.  Exactly one such result expected per
       relaxed_crystal.
    4. relax_dynamic:at_temp calculations ran where the temperature is
       iteratively increased and the previous temperature's relaxed structure is
       loaded as the parent structure.
    5. Optionally, one free_energy calculation and one elastic_constants_dynamic
       calculation ran for each finished relax_dynamic:at_temp(_50K) calculation.
    6. Call this function to build the md_solid_properties, one for each
       relax_dynamic:at_temp(_50K) calculation and merge in any associated
       results from the other calculation methods.

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
                                               potential_LAMMPS_id=potential_LAMMPS_id)
    if verbose:
        print(len(results), 'md_solid_properties records found', flush=True)
        print(len(results[results_df.method.isin(['at_temp', 'at_temp_50K'])]), 'are at_temp(_50K)')

    # Fetch finished relax_dynamic:at_temp(_50K) results 
    relaxes, relaxes_df = database.get_records('calculation_relax_dynamic', return_df=True,  
                                                branch=['at_temp', 'at_temp_50K'],
                                                status='finished',
                                                potential_LAMMPS_id=potential_LAMMPS_id)
    if verbose:
        print(len(relaxes), 'relax_dynamic:at_temp(_50K) records found', flush=True)

    # Fetch finished free_energy results 
    free_energies, free_energies_df = database.get_records('calculation_free_energy', return_df=True, 
                                                           status='finished',
                                                           potential_LAMMPS_id=potential_LAMMPS_id)
    if verbose:
        print(len(free_energies), 'free_energy records found', flush=True)

    # Fetch finished elastic_constants_dynamic results
    cijs, cijs_df = database.get_records('calculation_elastic_constants_dynamic', return_df=True,
                                         status='finished',  
                                         potential_LAMMPS_id=potential_LAMMPS_id)
    if verbose:
        print(len(cijs), 'elastic_constants_dynamic records found', flush=True)




    count_add = 0
    count_update = 0

    # Loop over each 50 K relax_dynamic record
    for index in tqdm(relaxes_df[relaxes_df.branch == 'at_temp_50K'].index):
        relax = relaxes[index]
        
        ############ Extract data from 0 K and 50 K records ##################
        
        # Pull out the size multiplier to scale box dimensions of higher temps
        sizemult = relax.system_mods.sizemults[0][1]
        
        # relax_dynamic:at_temp_50K records have relaxed_crystal records as parents
        relaxed_crystal_key = relaxes_df.loc[index, 'parent_key']
        
        # Find the associated 0K md_solid_properties to get the correct natoms
        parent_df = results_df[(results_df.relaxed_crystal_key == relaxed_crystal_key) & (results_df.method == '0K')]
        if len(parent_df) == 0:
            print(f'No 0K md_solid_results found for relaxed_crystal key {relaxed_crystal_key}, relax_dynamic key {relax.key}!')
            continue
        elif len(parent_df) > 1:
            raise ValueError(f'Multiple 0K results with relaxed_crystal key {relaxed_crystal_key}!')
        natoms = results_df.loc[parent_df.index[0], 'natoms']
        
        
        
        ############ Iterate through the relax_dynamic results to higher temps ###########
        
        while relax is not None:
            updated = False

            # Search for an existing md_solid_properties record
            match = results_df[
                #(results_df.potential_LAMMPS_key == relax.potential.potential_LAMMPS_key) &
                #(results_df.potential_key == relax.potential.potential_key) &
                (results_df.relax_dynamic_key == relax.key)]

            if len(match) == 0:
                # Create a new md_solid_properties record and add crystal info
                solid = am.library.load_record('md_solid_properties')
                solid.new_name()
                solid.extract_relax_dynamic(relax, relaxed_crystal_key, sizemult, natoms)
                updated = True

            elif len(match) == 1:
                # Get an existing md_solid_properties record
                solid = results[match.index[0]]

            else:
                raise ValueError('Multiple matches!!!')

            # Add Cij values if they exist and are not already in the md_solid_properties
            if solid.C is None:
                match = cijs_df[cijs_df.parent_key == relax.key]

                if len(match) == 1:
                    cij = cijs[match.index[0]]
                    solid.extract_elastic_constants(cij)
                    updated = True
                elif len(match) > 1:
                    print('multiple Cij!')

            # Add free energy values if they exist and are not already in the md_solid_properties
            if solid.gibbs is None:
                match = free_energies_df[free_energies_df.parent_key == relax.key]

                if len(match) == 1:
                    free_energy = free_energies[match.index[0]]
                    solid.extract_free_energy(free_energy)
                    updated = True
                elif len(match) > 1:
                    print('multiple free energies!')

            # Add/update record in the database if needed
            if updated:
                solid.build_model()
                try:
                    database.add_record(solid)
                    count_add += 1
                except:
                    database.update_record(solid)
                    count_update += 1
            
            
            # Find the next relaxation calculation in line
            child_df = relaxes_df[relaxes_df.parent_key == relax.key]
            if len(child_df) == 0:
                relax = None
            elif len(child_df) > 1:
                raise ValueError(f'Multiple children of {relax.key}!!!')
            else:
                relax = relaxes[child_df.index[0]]
                

    if verbose:
        print(count_add, 'records added')
        print(count_update, 'records updated')

    return count_add, count_update