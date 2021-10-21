import potentials

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

import numpy as np

__all__ = ['atomicparent']

def atomicparent(database, keys, content_dict=None, record=None,
                 load_key='atomic-system', **kwargs):
    
    # Initialize inputs and content dict
    inputs = {}
    for key in keys:
        inputs[key] = []
    if content_dict is None:
        content_dict = {}

    # Check if potential info is in keys
    if 'potential_file' in keys or 'potential_content' in keys or 'potential_dir' in keys:
        include_potentials = True
        
        # Extract kwargs starting with "potential"
        potkwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potkwargs[key[10:]] = kwargs.pop(key)

        # Set all status value
        if 'status' in potkwargs and potkwargs['status'] == 'all':
            potkwargs['status'] = None

        # Fetch potential records 
        potdb = potentials.Database(local_database=database, local=True, remote=False)
        lmppots, lmppots_df = potdb.get_lammps_potentials(return_df=True, **potkwargs)
        print(len(lmppots_df), 'matching interatomic potentials found')
        if len(lmppots_df) == 0:
            return inputs, content_dict
        kwargs['potential_LAMMPS_key'] = list(np.unique(lmppots_df.key))          

    else:
        include_potentials = False
    
    # Fetch reference records
    parents, parent_df = database.get_records(style=record, return_df=True,
                                              **kwargs)
    print(len(parent_df), 'matching atomic parents found')    
    if len(parent_df) == 0:
        return inputs, content_dict

    # Loop over all parents
    for i in parent_df.index:
        parent = parents[i]
        parent_series = parent_df.loc[i]
        content_dict[parent.name] = parent.build_model()
        
        # Find potential
        if include_potentials:
            try:
                potential_LAMMPS_id = parent_series.potential_LAMMPS_id
            except:
                # Search grandparents for name of potential
                potential_LAMMPS_id = None
                for grandparent in database.get_parent_records(record=parent):
                    try:
                        potential_LAMMPS_id = grandparent.todict(full=False, flat=True)['potential_LAMMPS_id']
                    except:
                        pass
                    else:
                        break
                if potential_LAMMPS_id is None:
                    raise ValueError('potential info not found')
            try:
                lmppot_series = lmppots_df[lmppots_df.id == potential_LAMMPS_id].iloc[0]
            except:
                continue
            
            lmppot = lmppots[lmppot_series.name]
            content_dict[lmppot.name] = lmppot.build_model()

        # Determine number of systems in parent to iterate over
        if 'status' not in parent_series or parent_series.status == 'finished':
            if 'load_options' in keys:
                nparents = len(parent.build_model().finds(load_key))
            else:
                nparents = 1
        elif parent_series.status == 'not calculated':
            nparents = 1
        elif parent_series.status == 'error':
            nparents = 0
        else:
            raise ValueError('Unsupported record status')
        
        # Loop over each system in parent
        for j in range(nparents):
            
            # Loop over input keys
            for key in keys:
                if key == 'potential_file':
                    inputs['potential_file'].append(f'{lmppot.name}.json')
                elif key == 'potential_content':
                    inputs['potential_content'].append(f'record {lmppot.name}')
                elif key == 'potential_dir' and lmppot.pair_style != 'kim':
                    inputs['potential_dir'].append(lmppot.name)
                elif key == 'potential_dir_content' and lmppot.pair_style != 'kim':
                    inputs['potential_dir_content'].append(f'tar {lmppot.name}')
                elif key == 'potential_kim_id' and lmppot.pair_style == 'kim':
                    inputs['potential_kim_id'].append(lmppot.id)
                elif key == 'potential_kim_potid' and lmppot.pair_style == 'kim' and len(lmppot.potids) > 1:
                    inputs['potential_kim_potid'].append(lmppot.potid)
                elif key == 'load_file':
                    inputs['load_file'].append(f'{parent.name}.json')
                elif key == 'load_content':
                    inputs['load_content'].append(f'record {parent.name}')
                elif key == 'load_style':
                    inputs['load_style'].append('system_model')
                elif key == 'load_options':
                    if j == 0:
                        inputs['load_options'].append(f'key {load_key}')
                    else:
                        inputs['load_options'].append(f'key {load_key} index {j}')
                elif key == 'family':
                    inputs['family'].append(parent_series.family)
                elif key == 'elasticconstants_file':
                    inputs['elasticconstants_file'].append(f'{parent.name}.json')
                elif key == 'elasticconstants_content':
                    inputs['elasticconstants_content'].append(f'record {parent.name}')
                else:
                    inputs[key].append('')
    
    return inputs, content_dict