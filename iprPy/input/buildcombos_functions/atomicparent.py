# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# iprPy imports
from ...compatibility import range
from .interatomicpotential import interatomicpotential

__all__ = ['atomicparent']

def atomicparent(database, keys, record=None, load_key='atomic-system',
                 query=None, **kwargs):
    
    # Setup
    inputs = {}
    for key in keys:
        inputs[key] = []
    if 'potential_file' in keys:
        include_potential = True
    else:
        include_potential = False
    
    # Loop over all matching records
    parent_records = database.get_records(style=record, query=query, **kwargs)
    
    for parent_record in parent_records:
        parent = parent_record.content
        family = parent.find('system-info')['family']
        
        name = parent_record.name
        
        # Count number of load keys in parent
        nparents = len(parent.finds(load_key))
        
        # Prepare once for unfinished parents
        if nparents == 0:
            try:
                status = parent.find('status')
            except:
                status = 'finished'
            if status == 'not calculated':
                nparents = 1
        
        # Add parent info containing system_model information
        for j in range(nparents):
            if j == 0:
                load_options = 'key ' + load_key
            else:
                load_options = 'key ' + load_key + ' index ' + str(j)
            
            inputs['load_file'].append(name + '.json')
            inputs['load_content'].append('record ' + name)
            inputs['load_style'].append('system_model')
            inputs['load_options'].append(load_options)
            inputs['family'].append(family)
            inputs['symbols'].append('')
            inputs['box_parameters'].append('')
            
            # Extract potential information
            if include_potential is True:
                try:
                    # Get name of potential from parent
                    potential_name = parent.find('potential-LAMMPS')['id']
                except:
                    # Search grandparents for name of potential
                    potential_name = None
                    for grandparent_record in database.get_parent_records(record=parent_record):
                        grandparent = grandparent_record.content
                        try:
                            potential_name = grandparent.find('potential-LAMMPS')['id']
                        except:
                            pass
                        else:
                            break
                    if potential_name is None:
                        raise ValueError('potential info not found')
                
                inputs['potential_file'].append(potential_name + '.json')
                inputs['potential_content'].append(database.get_record(name=potential_name).content.json(indent=4))
                inputs['potential_dir'].append(potential_name)
    
    return inputs