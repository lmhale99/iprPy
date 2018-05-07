# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# http://www.numpy.org/
import numpy as np

__all__ = ['interatomicpotential']

def interatomicpotential(database, keys=['potential_file', 'potential_content', 'potential_dir'],
          record='potential_LAMMPS', currentIPR=True, query=None, **kwargs):
    """
    Builds parameter sets related to interatomic potentials.
    """
    potentials, potential_df = database.get_records(style=record, return_df=True,
                                                    query=query, **kwargs)
    
    
    potential_content = []
    for potential in potentials:
        potential_content.append(potential.content)
    potential_df['content'] = potential_content
    
    # Limit to only current IPR implementations
    if currentIPR is True:
        
        # Extract versionstyle and versionnumber
        versionstyle = []
        versionnumber = []
        for name in potential_df['id'].values:
            version = name.split('--')[-1]
            try:
                versionnumber.append(int(version[-1]))
            except:
                versionnumber.append(np.nan)
                versionstyle.append(version)
            else:
                versionstyle.append(version[:-1])
        
        potential_df['versionstyle'] = versionstyle
        potential_df['versionnumber'] = versionnumber
        
        # Loop through unique potential id's
        includeid = []
        for pot_id in np.unique(potential_df.pot_id.values):
            check_df = potential_df[potential_df.pot_id == pot_id]
            check_df = check_df[check_df.versionstyle == 'ipr']
            check_df = check_df[check_df.versionnumber == check_df.versionnumber.max()]
            if len(check_df) == 1:
                includeid.append(check_df['id'].values[0])
            elif len(check_df) > 1:
                raise ValueError('Bad currentIPR check for '+pot_id)
        
        # Limit df by includeid potentials
        potential_df = potential_df[potential_df['id'].isin(includeid)]
    
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    for i, potential_series in potential_df.iterrows():
        inputs['potential_file'].append(potential_series.id + '.json')
        #inputs['potential_content'].append('record ' + potential_series.id)
        inputs['potential_content'].append(potential_series.content.json(indent=4))
        inputs['potential_dir'].append(potential_series.id)
    
    return inputs