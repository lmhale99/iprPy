# http://www.numpy.org/
import numpy as np

__all__ = ['interatomicpotential']

def interatomicpotential(database, keys, content_dict=None, record='potential_LAMMPS',
                         status='active', query=None, **kwargs):
    """
    Builds parameter sets related to interatomic potentials.
    """
    # Initialize inputs and content dict
    inputs = {}
    for key in keys:
        inputs[key] = []
    if content_dict is None:
        content_dict = {}

    # Set all status value
    if status == 'all':
        status = ['active', 'retracted', 'superseded']

    # Fetch potential records and df
    potentials, potential_df = database.get_records(style=record, return_df=True,
                                                    query=query, status=status, **kwargs)
    print(len(potential_df), 'matching interatomic potentials found')
    if len(potential_df) == 0:
        return inputs, content_dict
    
    # Loop over all potentials 
    for i in potential_df.index:
        potential = potentials[i]
        content_dict[potential.name] = potential.content

        # Loop over all input keys
        for key in keys:
            if key == 'potential_file':
                inputs['potential_file'].append(f'{potential.name}.json')
            elif key == 'potential_content':
                inputs['potential_content'].append(f'record {potential.name}')
            elif key == 'potential_dir':
                inputs['potential_dir'].append(potential.name)
            elif key == 'potential_dir_content':
                inputs['potential_dir_content'].append(f'tar {potential.name}')
            else:
                inputs[key].append('')

    return inputs, content_dict