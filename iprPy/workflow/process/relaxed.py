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

    # Load relax_box records
    raw_df = database.get_records_df(style='calculation_relax_box',
                                    full=True, flat=True)
    print(f'{len(raw_df)} calculation_relax_box records found', flush=True)

    if len(raw_df) > 0:
        box_df = raw_df[raw_df.branch=='main'].reset_index(drop=True)
        box_df['method'] = 'box'
        print(f" - {len(box_df)} are branch main", flush=True)
    else:
        box_df = pd.DataFrame()

    # Load relax_static records      
    raw_df = database.get_records_df(style='calculation_relax_static',
                                    full=True, flat=True)
    print(f'{len(raw_df)} calculation_relax_static records found', flush=True)

    if len(raw_df) > 0:
        static_df = raw_df[raw_df.branch=='main'].reset_index(drop=True)
        static_df['method'] = 'static'
        print(f" - {len(static_df)} are branch main", flush=True)
        dynamic_df = raw_df[raw_df.branch=='from_dynamic'].reset_index(drop=True)
        dynamic_df['method'] = 'dynamic'
        print(f" - {len(dynamic_df)} are branch from_dynamic", flush=True)
    else:
        static_df = pd.DataFrame()
        dynamic_df = pd.DataFrame()

    parent_df = pd.concat([box_df, static_df, dynamic_df], ignore_index=True, sort=False)

    # Get space group results
    spg_records = database.get_records_df(style='calculation_crystal_space_group',
                                        full=True, flat=False, status='finished')
    print(f'{len(spg_records)} calculation_crystal_space_group records found',
        flush=True)

    if len(spg_records) > 0:
        
        # Separate records using branch
        prototype_records = spg_records[spg_records.branch == 'prototype']
        print(f' - {len(prototype_records)} are for prototypes', flush=True)
        
        reference_records = spg_records[spg_records.branch == 'reference']
        print(f' - {len(reference_records)} are for references', flush=True)
        
        family_records = spg_records[(spg_records.branch == 'prototype') 
                                    |(spg_records.branch == 'reference')]
        
        calc_records = spg_records[spg_records.branch == 'relax'].reset_index(drop=True)
        print(f' - {len(calc_records)} are for calculations', flush=True)

    else:
        print('Stopping as no calculations to process')

    if len(calc_records) == 0:
        print('Stopping as no calculations to process')
        
    if len(family_records) == 0:
        print('Stopping as prototype/reference records needed')

    # Get existing relaxed_records
    relaxed_records = database.get_records_df(style='relaxed_crystal', full=True, flat=False)
    print(len(relaxed_records), 'relaxed records found')
    print(f' - {len(relaxed_records[relaxed_records.standing=="good"])} good and unique')

    # !!!!!!!!!!!!!!!!!!!!!!!!!! Load saved results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    # Load crystal_match_file
    try:
        ref_proto_match = pd.read_csv(crystal_match_file)
    except:
        columns = ['reference', 'prototype', 'composition']
        ref_proto_match = pd.DataFrame(columns=columns)
    print(f'{len(ref_proto_match)} references matched to prototypes', flush=True)

    # !!!!!!!!!!!!!!! Merge DataFrames and extract  results !!!!!!!!!!!!!!!!!!!!! #

    # Get parent keys (relax_*) for space_group calculations
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

    # Identify transformed structures by comparing spacegroup info before/after relax
    def get_transformed(series):
        return (not (series.spacegroup_number_family == series.spacegroup_number
                    and series.pearson_symbol_family == series.pearson_symbol))
    results['transformed'] = merged_df.apply(get_transformed, axis=1)

    # Set prototype as prototype (if given) or family
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
    results_keys = ['calc_key', 'potential_LAMMPS_key', 'potential_LAMMPS_id', 'potential_key',
                    'potential_id', 'composition', 'prototype', 'family', 'parent_key', 'method',
                    'transformed', 'E_coh', 'a', 'b', 'c', 'alpha', 'beta', 'gamma', 'ucell', 'ucell_family']
    sort_keys = ['potential_LAMMPS_id', 'composition', 'prototype', 'family', 'E_coh']
    results = pd.DataFrame(results, columns=results_keys).sort_values(sort_keys)
    results[results_keys[:-2]].to_csv(all_crystals_file, index=False)
    print(all_crystals_file, 'updated')

    # !!!!!!!!!!!!!!!! Add new records to relaxed_crystal !!!!!!!!!!!!!!! #

    results = results[~results.transformed]
    print(len(results), 'results remained untransformed')

    results['added'] = results.calc_key.isin(relaxed_records.parent_key)

    def set_parent_type(series):
        if series.family[0] == 'm' or series.family[0] == 'o':
            return 'reference'
        else:
            return 'prototype'
    results['parent_type'] = results.apply(set_parent_type, axis=1)

    def set_method_int(series):
        if series.method == 'dynamic':
            return 1
        elif series.method == 'static':
            return 2
        else:
            return 3
    results['method_int'] = results.apply(set_method_int, axis=1)

    newresults = results[~results['added']]
    print(f' - {len(newresults)} new results to add')

    # Loop over all new records
    for i, series in newresults.sort_values(['method_int', 'parent_type']).iterrows():
        oldresults = results[results.added]
        
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
        
        # Set potential
        potential_record = database.get_record(style='potential_LAMMPS', key=series.potential_LAMMPS_key)
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
        
        # Check for existing duplicates
        matches = (
            (series.potential_LAMMPS_key == oldresults.potential_LAMMPS_key)
        &(series.composition == oldresults.composition)
        &np.isclose(series.E_coh, oldresults.E_coh)
        &np.isclose(series.a, oldresults.a)
        &np.isclose(series.b, oldresults.b)
        &np.isclose(series.c, oldresults.c)
        &np.isclose(series.alpha, oldresults.alpha)
        &np.isclose(series.beta, oldresults.beta)
        &np.isclose(series.gamma, oldresults.gamma))
        
        # Set standing
        if series.E_coh < -1e-5 and matches.sum() == 0:
            input_dict['standing'] = 'good'
        else:
            input_dict['standing'] = 'bad'
        
        # Build content and upload
        record.buildcontent('noscript', input_dict)
        database.add_record(record=record)

    relaxed_records = database.get_records_df(style='relaxed_crystal', full=True, flat=False)
    print(len(relaxed_records), 'relaxed records found')
    print(f' - {len(relaxed_records[relaxed_records.standing=="good"])} good and unique')

    unique_results = pd.merge(results, relaxed_records, left_on='calc_key', right_on='parent_key', suffixes=('', '_dup'), validate='one_to_one')
    unique_results = unique_results[unique_results.standing=='good'].sort_values(sort_keys)

    unique_results[results_keys[:-2]].to_csv(unique_crystals_file, index=False)
    print(unique_crystals_file, 'updated')