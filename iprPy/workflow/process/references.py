# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

from ... import load_database

def references(database_name, crystal_match_file):

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! Load records !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    database = load_database(database_name)

    # Load crystal_prototype records
    #proto_records = database.get_records_df(style='crystal_prototype')
    #print(f'{len(proto_records)} prototype records found', flush=True)

    # Load reference_crystal records
    ref_records = database.get_records_df(style='reference_crystal')
    print(f'{len(ref_records)} reference records found', flush=True)

    # Load crystal_space_group results
    spg_records = database.get_records_df(style='calculation_crystal_space_group',
                                          full=True, flat=False, status='finished')
    print(f'{len(spg_records)} calculation_crystal_space_group records found',
          flush=True)

    # build lists of load_files from proto and ref parents
    #proto_parents = []
    #for proto in proto_records.id:
    #    proto_parents.append(f'{proto}.json')
    ref_parents = []
    for ref in ref_records.id:
        ref_parents.append(f'{ref}.json')

    # Identify record_type as calc, reference or prototype
    #spg_records['record_type'] = 'calc'
    #spg_records.loc[spg_records.load_file.isin(proto_parents), 'record_type'] = 'prototype'
    #spg_records.loc[spg_records.load_file.isin(ref_parents), 'record_type'] = 'reference'

    # Separate out reference records
    reference_records = spg_records[spg_records.load_file.isin(ref_parents)]
    print(f' -{len(reference_records)} are for references', flush=True)

    # !!!!!!!!!!!!!!!!!!!!!!!!!! Load saved results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    try: 
        ref_proto_match = pd.read_csv(crystal_match_file)
    except:
        columns = ['reference', 'prototype', 'composition', 'site', 'number']
        ref_proto_match = pd.DataFrame(columns=columns)
    else:
        sites = []
        numbers = []
        for series in ref_proto_match.itertuples():
            site, number = series.reference.split('-')
            sites.append(site)
            numbers.append(int(number))
        ref_proto_match['site'] = sites
        ref_proto_match['number'] = numbers
    print(f'{len(ref_proto_match)} previous reference-prototype matches found', flush=True)

    # !!!!!!!!!!!!!!!!!!!!!!!!! Process new results !!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    newmatch = []
    for ref_record in reference_records.itertuples():
        if ref_record.family in ref_proto_match.reference.tolist():
            continue

        ref_proto_dict = {}
        ref_proto_dict['reference'] = ref_record.family
        ref_proto_dict['composition'] = ref_record.composition
        ref_proto_dict['site'], ref_proto_dict['number'] = ref_record.family.split('-')
        ref_proto_dict['number'] = int(ref_proto_dict['number'])
        
        # Find matching prototypes based on spg number and wykoffs
        prototype = np.nan
        
        # A1--Cu--fcc
        if (ref_record.spacegroup_number == 225 
        and ref_record.wykoff_fingerprint in ['a', 'b']):
            prototype = 'A1--Cu--fcc'
        
        # A2--W--bcc
        elif (ref_record.spacegroup_number == 229 
        and ref_record.wykoff_fingerprint in ['a']):
            prototype = 'A2--W--bcc'
        
        # A3'--alpha-La--double-hcp
        elif (ref_record.spacegroup_number == 194
        and ref_record.wykoff_fingerprint in ['ab', 'ac', 'ad']):
            prototype = "A3'--alpha-La--double-hcp"
        
        # A3--Mg--hcp
        elif (ref_record.spacegroup_number == 194
        and ref_record.wykoff_fingerprint in ['b', 'c', 'd']):
            prototype = 'A3--Mg--hcp'
            
        # A4--C--dc
        elif (ref_record.spacegroup_number == 227
        and ref_record.wykoff_fingerprint in ['a', 'b']):
            prototype = 'A4--C--dc'
        
        # A5--beta-Sn
        elif (ref_record.spacegroup_number == 141
        and ref_record.wykoff_fingerprint in ['a', 'b']):
            prototype = 'A5--beta-Sn'
        
        # A6--In--bct
        elif (ref_record.spacegroup_number == 139
        and ref_record.wykoff_fingerprint in ['a', 'b']):
            prototype = 'A6--In--bct'
            
        # A7--alpha-As
        elif (ref_record.spacegroup_number == 166
        and ref_record.wykoff_fingerprint in ['c']):
            prototype = 'A7--alpha-As'
            
        # A15--beta-W
        elif (ref_record.spacegroup_number == 223
        and ref_record.wykoff_fingerprint in ['ac', 'ad']):
            prototype = 'A15--beta-W'
        
        # A15--Cr3Si
        elif (ref_record.spacegroup_number == 223
        and ref_record.wykoff_fingerprint in ['a c', 'c a', 'a d', 'd a']):
            prototype = 'A15--Cr3Si'
        
        # Ah--alpha-Po--sc
        elif (ref_record.spacegroup_number == 221
        and ref_record.wykoff_fingerprint in ['a', 'b']):
            prototype = 'Ah--alpha-Po--sc'
        
        # B1--NaCl--rock-salt
        elif (ref_record.spacegroup_number == 225
        and ref_record.wykoff_fingerprint in ['a b', 'b a']):
            prototype = 'B1--NaCl--rock-salt'
        
        # B2--CsCl
        elif (ref_record.spacegroup_number == 221
        and ref_record.wykoff_fingerprint in ['a b', 'b a']):
            prototype = 'B2--CsCl'
        
        # B3--ZnS--cubic-zinc-blende
        elif (ref_record.spacegroup_number == 216
        and ref_record.wykoff_fingerprint in ['a c', 'c a', 'b d', 'd b', 'a d', 'd a', 'b c', 'c b']):
            prototype = 'B3--ZnS--cubic-zinc-blende'
        
        # C1--CaF2--fluorite
        elif (ref_record.spacegroup_number == 225
        and ref_record.wykoff_fingerprint in ['a c', 'c a', 'b c', 'c b']):
            prototype = 'C1--CaF2--fluorite'
        
        # D0_3--BiF3
        elif (ref_record.spacegroup_number == 225
        and ref_record.wykoff_fingerprint in ['a bc', 'bc a', 'b ac', 'ac b']):
            prototype = 'D0_3--BiF3'
        
        # L1_0--AuCu
        elif (ref_record.spacegroup_number == 123
        and ref_record.wykoff_fingerprint in ['a d', 'd a', 'b c', 'c b']):
            prototype = 'L1_0--AuCu'
        
        # L1_2--AuCu3
        elif (ref_record.spacegroup_number == 221
        and ref_record.wykoff_fingerprint in ['a c', 'c a', 'b d', 'd b']):
            prototype = 'L1_2--AuCu3'
        
        # L2_1--AlCu2Mn--heusler
        elif (ref_record.spacegroup_number == 225
        and ref_record.wykoff_fingerprint in ['a b c', 'b c a', 'c a b', 'a c b', 'c b a', 'b a c']):
            prototype = 'L2_1--AlCu2Mn--heusler'
        
        ref_proto_dict['prototype'] = prototype
        newmatch.append(ref_proto_dict)
    
    print(f'{len(newmatch)} new results added')
    if len(newmatch) > 0:
        ref_proto_match = ref_proto_match.append(newmatch, ignore_index=True)
        ref_proto_match = ref_proto_match.sort_values(['site', 'number']).reset_index()
        ref_proto_match = ref_proto_match[['reference', 'prototype', 'composition']]
        ref_proto_match.to_csv(crystal_match_file, index=False)