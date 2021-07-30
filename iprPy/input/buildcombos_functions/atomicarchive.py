# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

import potentials

import numpy as np

__all__ = ['atomicarchive']

def atomicarchive(database, keys, content_dict=None, record=None, load_key='atomic-system',
                  **kwargs):
    """
    Build parameter sets based on loading files from within a calculation tar archive.
    """
    # Initialize inputs and content dict
    inputs = {}
    for key in keys:
        inputs[key] = []
    if content_dict is None:
        content_dict = {}

    # Check if potential info is in keys
    if 'potential_file' in keys:
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
    print(len(parent_df), 'matching atomic archives found')
    if len(parent_df) == 0:
        return inputs, content_dict

    # Loop over all parents
    for i in parent_df.index:
        parent = parents[i]
        parent_series = parent_df.loc[i]
        
        # Find potential
        if include_potentials:
            try:
                potential_LAMMPS_key = parent_series.potential_LAMMPS_key
            except:
                # Search grandparents for name of potential
                potential_LAMMPS_key = None
                for grandparent in database.get_parent_records(record=parent):
                    try:
                        potential_LAMMPS_key = grandparent.todict(full=False, flat=True)['potential_LAMMPS_key']
                    except:
                        pass
                    else:
                        break
                if potential_LAMMPS_key is None:
                    raise ValueError('potential info not found')
            try:
                lmppot_series = lmppots_df[lmppots_df.key == potential_LAMMPS_key].iloc[0]
            except:
                continue
            lmppot = lmppots[lmppot_series.name]
            content_dict[lmppot.name] = lmppot.build_model()
        
        # Loop over each system in parent
        for load_info in parent.build_model().finds(load_key):
            
            # Extract system load info
            load_file = load_info['artifact']['file']
            load_style = load_info['artifact']['format']
            load_options = load_info['artifact'].get('load_options', '')
            symbols = ' '.join(load_info.aslist('symbols'))

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
                elif key == 'load_file':
                    inputs['load_file'].append(f'{parent.name}/{load_file}')
                elif key == 'load_content':
                    inputs['load_content'].append(f'tarfile {parent.name} {load_file}')
                elif key == 'load_style':
                    inputs['load_style'].append(load_style)
                elif key == 'load_options':
                    inputs['load_options'].append(load_options)
                elif key == 'symbols':
                    inputs['symbols'].append(symbols)
                elif key == 'family':
                    inputs['family'].append(parent_series.family)
                elif key == 'elasticconstants_file':
                    inputs['elasticconstants_file'].append(f'{parent.name}.json')
                elif key == 'elasticconstants_content':
                    inputs['elasticconstants_content'].append(f'record {parent.name}')
                else:
                    inputs[key].append('')
    
    return inputs, content_dict