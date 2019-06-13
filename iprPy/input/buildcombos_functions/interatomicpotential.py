# http://www.numpy.org/
import numpy as np

from ...analysis import assign_currentIPR

__all__ = ['interatomicpotential']

def interatomicpotential(database, keys, content_dict=None, record='potential_LAMMPS',
                         currentIPR=None, query=None, **kwargs):
    """
    Builds parameter sets related to interatomic potentials.
    """
    if content_dict is None:
        content_dict = {}

    # Default currentIPR is True for default record, False otherwise
    if currentIPR is None:
        currentIPR = record == 'potential_LAMMPS'
    
    # Fetch potential records and df
    potentials, potential_df = database.get_records(style=record, return_df=True,
                                                    query=query, **kwargs)
    
    # Filter by currentIPR (note that DataFrame index is unchanged)
    if currentIPR:
        assign_currentIPR(pot_df=potential_df)
        potential_df = potential_df[potential_df.currentIPR == True]

    # Initialize inputs keys
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    # Loop over all potentials 
    for i, potential_series in potential_df.iterrows():
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