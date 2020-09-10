# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

__all__ = ['atomicarchive']

def atomicarchive(database, keys, content_dict=None, record=None, load_key='atomic-system',
                  query=None, **kwargs):

    if content_dict is None:
        content_dict = {}

    # Check if potential info is in keys
    if 'potential_file' in keys or 'potential_dir' in keys:
        include_potentials = True
        
        # Extract kwargs starting with "potential"
        potential_kwargs = {}
        for key in list(kwargs.keys()):
            if key[:10] == 'potential_':
                potential_kwargs[key[10:]] = kwargs.pop(key)

        # Pull out potential get_records parameters
        potential_record = potential_kwargs.pop('record', 'potential_LAMMPS')
        potential_query = potential_kwargs.pop('query', None)
        status = potential_kwargs.pop('status', 'active')
        
        # Set all status value
        if status is 'all':
            status = ['active', 'retracted', 'superseded']
        
        # Fetch potential records 
        potentials, potential_df = database.get_records(style=potential_record, return_df=True,
                                                        query=potential_query, status=status,
                                                        **potential_kwargs)
        print(len(potential_df), 'matching interatomic potentials found')
        if len(potential_df) == 0:
            raise ValueError('No matching interatomic potentials found') 
    else:
        include_potentials = False

    # Fetch reference records
    parents, parent_df = database.get_records(style=record, return_df=True,
                                              query=query, **kwargs)
    print(len(parent_df), 'matching atomic archives found')
    if len(parent_df) == 0:
        raise ValueError('No matching atomic archives found')

    # Setup
    inputs = {}
    for key in keys:
        inputs[key] = []   

    # Loop over all parents
    for i in parent_df.index:
        parent = parents[i]
        parent_series = parent_df.loc[i]
        
        # Find potential
        if include_potentials:
            try:
                potential_id = parent_series.potential_LAMMPS_id
            except:
                # Search grandparents for name of potential
                potential_id = None
                for grandparent in database.get_parent_records(record=parent):
                    try:
                        potential_id = grandparent.todict(full=False, flat=True)['potential_LAMMPS_id']
                    except:
                        pass
                    else:
                        break
                if potential_id is None:
                    raise ValueError('potential info not found')
            try:
                potential_series = potential_df[potential_df.id == potential_id].iloc[0]
            except:
                continue
            potential = potentials[potential_series.name]
            content_dict[potential.name] = potential.content
        
        # Loop over each system in parent
        for load_info in parent.content.finds(load_key):
            
            # Extract system load info
            load_file = load_info['artifact']['file']
            load_style = load_info['artifact']['format']
            load_options = load_info['artifact'].get('load_options', '')
            symbols = ' '.join(load_info.aslist('symbols'))

            # Loop over input keys
            for key in keys:
                if key == 'potential_file':
                    inputs['potential_file'].append(f'{potential.name}.json')
                elif key == 'potential_content':
                    inputs['potential_content'].append(f'record {potential.name}')
                elif key == 'potential_dir':
                    inputs['potential_dir'].append(potential.name)
                elif key == 'potential_dir_content':
                    inputs['potential_dir_content'].append(f'tar {potential.name}')
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