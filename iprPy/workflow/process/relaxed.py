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

def relaxed(database_name, crystal_match_file, all_crystals_file, unique_crystals_file):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! Load records !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    database = load_database(database_name)

    # Load potential_LAMMPS records
    pot_records = database.get_records_df(style='potential_LAMMPS')
    print(f'{len(pot_records)} potential records found', flush=True)

    # Load crystal_prototype records
    proto_records = database.get_records_df(style='crystal_prototype')
    print(f'{len(proto_records)} prototype records found', flush=True)

    # Load reference_crystal records
    ref_records = database.get_records_df(style='reference_crystal')
    print(f'{len(ref_records)} reference records found', flush=True)

    # Get key lists for relax_* calculations
    raw_df = database.get_records_df(style='calculation_relax_box',
                                    full=False, flat=True)
    print(f'{len(raw_df)} calculation_relax_box records found', flush=True)
    try:
        box_keys = raw_df.key.tolist()
    except:
        box_keys = []

    raw_df = database.get_records_df(style='calculation_relax_static',
                                    full=False, flat=True)
    print(f'{len(raw_df)} calculation_relax_static records found', flush=True)
    try:
        static_keys = raw_df.key.tolist()
    except:
        static_keys = []

    raw_df = database.get_records_df(style='calculation_relax_dynamic',
                                    full=False, flat=True)
    print(f'{len(raw_df)} calculation_relax_dynamic records found', flush=True)
    try:
        dynamic_keys = raw_df.key.tolist()
    except:
        dynamic_keys = []
    print()

    # Get space group results
    spg_records = database.get_records_df(style='calculation_crystal_space_group',
                                        full=True, flat=False, status='finished')
    print(f'{len(spg_records)} calculation_crystal_space_group records found',
        flush=True)

    if len(spg_records) == 0:
        print('Stopping as no calculations to process')
        return

    # build lists of load_files from proto and ref parents
    proto_parents = []
    for proto in proto_records.id:
        proto_parents.append(f'{proto}.json')
    ref_parents = []
    for ref in ref_records.id:
        ref_parents.append(f'{ref}.json')

    # Identify record_type as calc, reference or prototype
    spg_records['record_type'] = 'calc'
    spg_records.loc[spg_records.load_file.isin(proto_parents), 'record_type'] = 'prototype'
    spg_records.loc[spg_records.load_file.isin(ref_parents), 'record_type'] = 'reference'

    # Separate records by parent type
    prototype_records = spg_records[spg_records.record_type == 'prototype']
    reference_records = spg_records[spg_records.record_type == 'reference']
    family_records = spg_records[(spg_records.record_type == 'prototype') 
                                |(spg_records.record_type == 'reference')]
    print(f' -{len(prototype_records)} are for prototypes', flush=True)
    print(f' -{len(reference_records)} are for references', flush=True)

    calc_records = spg_records[spg_records.record_type == 'calc'].reset_index(drop=True)
    print(f' -{len(calc_records)} are for calculations', flush=True)
    print()

    if len(calc_records) == 0:
        print('Stopping as no calculations to process')
        return

    if len(family_records) == 0:
        print('Stopping as prototype/reference records needed')
        return

    # !!!!!!!!!!!!!!!!!!!!!!!!!! Load saved results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    try:
        ref_proto_match = pd.read_csv(crystal_match_file)
    except:
        columns = ['reference', 'prototype', 'composition']
        ref_proto_match = pd.DataFrame(columns=columns)
    print(f'{len(ref_proto_match)} references matched to prototypes', flush=True)

    try:
        results = pd.read_csv(all_crystals_file)
    except:
        columns = ['calc_key', 'potential_LAMMPS_key', 'potential_LAMMPS_id',
                'potential_key', 'potential_id', 'composition', 'prototype',
                'family', 'method', 'transformed', 'E_coh', 'a', 'b', 'c',
                    'alpha', 'beta', 'gamma']
        results = pd.DataFrame(columns=columns)
    print(f'{len(results)} previous results found', flush=True)

    try:
        unique = pd.read_csv(unique_crystals_file)
    except:
        columns = ['calc_key', 'potential_LAMMPS_key', 'potential_LAMMPS_id',
                'potential_key', 'potential_id', 'composition', 'prototype',
                'family', 'method', 'transformed', 'E_coh', 'a', 'b', 'c',
                    'alpha', 'beta', 'gamma']
        unique = pd.DataFrame(columns=columns)
    print(f'{len(unique)} previous unique results found', flush=True)

    print()

    # !!!!!!!!!!!!!!!!!!!!!!!!! Process new results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    newresults = []
    old_keys = results.calc_key.values
    for series in calc_records.itertuples():
        if series.key in old_keys:
            continue
            
        results_dict = {}
        
        # Copy over values in series    
        results_dict['calc_key'] = series.key
        results_dict['composition'] = series.composition
        results_dict['family'] = series.family
        results_dict['a'] = series.ucell.box.a
        results_dict['b'] = series.ucell.box.b
        results_dict['c'] = series.ucell.box.c
        results_dict['alpha'] = series.ucell.box.alpha
        results_dict['beta'] = series.ucell.box.beta
        results_dict['gamma'] = series.ucell.box.gamma
        
        # Identify prototype
        try:
            results_dict['prototype'] = ref_proto_match[ref_proto_match.reference==series.family].prototype.values[0]
        except:
            results_dict['prototype'] = series.family
        else:
            if pd.isnull(results_dict['prototype']):
                results_dict['prototype'] = series.family
        
        # Check if structure has transformed relative to reference
        family_series = family_records[family_records.family == series.family].iloc[0]
        results_dict['transformed'] = (not (family_series.spacegroup_number == series.spacegroup_number
                                    and family_series.pearson_symbol == series.pearson_symbol))
        
        # Extract info from parent calculations
        for parent in database.get_parent_records(name=series.key):
            
            parent_dict = parent.todict()

            if parent_dict['key'] in box_keys:
                results_dict['method'] = 'box'
                results_dict['E_coh'] = parent_dict['E_cohesive']
                results_dict['potential_LAMMPS_key'] = parent_dict['potential_LAMMPS_key']
                continue

            elif parent_dict['key'] in dynamic_keys:
                results_dict['method'] = 'dynamic'
                continue

            elif parent_dict['key'] in static_keys:
                results_dict['method'] = 'static'
                results_dict['E_coh'] = parent_dict['E_cohesive']
                results_dict['potential_LAMMPS_key'] = parent_dict['potential_LAMMPS_key']

        pot_record = pot_records[pot_records.key == results_dict['potential_LAMMPS_key']].iloc[0]
        results_dict['potential_id'] = pot_record.pot_id
        results_dict['potential_key'] = pot_record.pot_key
        results_dict['potential_LAMMPS_id'] = pot_record.id
        
        newresults.append(results_dict)

    print(f'{len(newresults)} new results added')
    if len(newresults) > 0:
        results = results.append(newresults, ignore_index=True)
        results.to_csv(all_crystals_file, index=False)

    # !!!!!!!!!!!!!!!!!!!!!!!!! Find unique results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    new_unique = pd.DataFrame(columns=results.columns)

    # Loop over all potential implementations
    for implememtation_key in np.unique(results.potential_LAMMPS_key):
        imp_results = results[results.potential_LAMMPS_key == implememtation_key]
        
        # Loop over all compositions
        for composition in np.unique(results.composition):
            comp_unique = unique[unique.composition == composition].reset_index(drop=True)
            comp_results = imp_results[imp_results.composition == composition]
            
            # Loop over all prototypes
            for prototype in np.unique(comp_results.prototype):
                proto_results = comp_results[comp_results.prototype == prototype]
                
                # Loop over calculation methods from most robust to least
                for method in ['dynamic', 'static', 'box']:
                    
                    # First try matching results where prototype == family
                    for i, series in proto_results[(proto_results.prototype == proto_results.family)
                                                &(proto_results.method == method)
                                                &(~proto_results.transformed)].iterrows():
                        try:
                            matches = comp_unique[(np.isclose(comp_unique.E_coh, series.E_coh))
                                                &(np.isclose(comp_unique.a, series.a))
                                                &(np.isclose(comp_unique.b, series.b))
                                                &(np.isclose(comp_unique.c, series.c))
                                                &(np.isclose(comp_unique.alpha, series.alpha))
                                                &(np.isclose(comp_unique.beta, series.beta))
                                                &(np.isclose(comp_unique.gamma, series.gamma))]
                        except:
                            matches = []
                        if len(matches) == 0:
                            comp_unique = comp_unique.append(series)
                            new_unique = new_unique.append(series)
                            
                    # Next try matching results where prototype != family
                    for i, series in proto_results[(proto_results.prototype != proto_results.family)
                                                &(proto_results.method == method)
                                                &(~proto_results.transformed)].iterrows():
                        try:
                            matches = comp_unique[(np.isclose(comp_unique.E_coh, series.E_coh))
                                                &(np.isclose(comp_unique.a, series.a))
                                                &(np.isclose(comp_unique.b, series.b))
                                                &(np.isclose(comp_unique.c, series.c))
                                                &(np.isclose(comp_unique.alpha, series.alpha))
                                                &(np.isclose(comp_unique.beta, series.beta))
                                                &(np.isclose(comp_unique.gamma, series.gamma))]
                        except:
                            matches = []
                        if len(matches) == 0:
                            comp_unique = comp_unique.append(series)
                            new_unique = new_unique.append(series)
                            
    print(f'{len(new_unique)} new unique results added')       
    if len(new_unique) > 0:
        unique = unique.append(new_unique)
        unique.to_csv(unique_crystals_file, index=False)

    # !!!!!!!!!!!!!!!!!!! Generate relaxed_crystal records !!!!!!!!!!!!!!!!!!!!!! #

    for row in new_unique.itertuples():
        
        crystal_terms = {}
        crystal_terms['key'] = str(uuid.uuid4())
        crystal_terms['method'] = row.method
        crystal_terms['family'] = row.family
        crystal_terms['length_unit'] = 'angstrom'
        
        pot_record = database.get_record(name = pot_records[pot_records.key == row.potential_LAMMPS_key].id)
        crystal_terms['potential'] = lmp.Potential(pot_record.content)
        
        c_record = calc_records[calc_records.key == row.calc_key].iloc[0]
        
        # Use spg crystals for ref and α-As
        if (row.prototype[:3] == 'mp-' or
            row.prototype[:4] == 'mvc-' or
            row.prototype[:5] == 'oqmd-' or
            row.prototype == 'A7--alpha-As'):
            crystal_terms['ucell'] = c_record.ucell
        
        # Use scaled prototype crystals for the rest
        else:
            p_record = proto_records[proto_records.id == row.prototype].iloc[0]
            crystal_terms['ucell'] = p_record.ucell
            crystal_terms['ucell'].symbols = c_record.symbols
            crystal_terms['ucell'].box_set(a=row.a, b=row.b, c=row.c, alpha=row.alpha, beta=row.beta, gamma=row.gamma, scale=True)
        
        relaxrecord = load_record('relaxed_crystal')
        relaxrecord.buildcontent('b', crystal_terms)
        relaxrecord.name = crystal_terms['key']
        
        database.add_record(relaxrecord)