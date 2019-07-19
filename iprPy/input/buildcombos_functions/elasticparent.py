# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# iprPy imports
from .interatomicpotential import interatomicpotential

__all__ = ['elasticparent']

def elasticparent(database, keys, content_dict=None, record=None,
                  load_key='atomic-system', query=None, **kwargs):
    
    if content_dict is None:
        content_dict = {}
    
    # Setup
    inputs = {}
    for key in keys:
        inputs[key] = []
    
    if 'potential_file' in keys:
        include_potential = True
    else:
        include_potential = False
    
    if 'elasticconstants_file' in keys:
        include_elastic = True
    else:
        include_elastic = False
    
    # Loop over all matching records
    parent_records = database.get_records(style=record, query=query, **kwargs)
    for parent_record in parent_records:
        parent = parent_record.content
        
        # Loop over load_keys
        for load_info in parent.finds(load_key):
            
            name = parent_record.name
            file = load_info['artifact']['file']
            style = load_info['artifact']['format']
            options = load_info['artifact'].get('load_options', '')
            try:
                family = load_info['family']
            except:
                family = parent.find('system-info')['family']
            
            # Extract load information
            inputs['load_file'].append(name + '/' + file)
            inputs['load_content'].append('tar ' + name + ' ' + file)
            inputs['load_style'].append(style)
            inputs['load_options'].append(options)
            inputs['family'].append(family)
            inputs['symbols'].append(' '.join(load_info.aslist('symbols')))
            inputs['box_parameters'].append('')
            inputs['elasticconstants_file'].append(name + '.json')
            inputs['elasticconstants_content'].append('record ' + name)
            inputs['C11'].append('')
            inputs['C12'].append('')
            inputs['C13'].append('')
            inputs['C14'].append('')
            inputs['C15'].append('')
            inputs['C16'].append('')
            inputs['C22'].append('')
            inputs['C23'].append('')
            inputs['C24'].append('')
            inputs['C25'].append('')
            inputs['C26'].append('')
            inputs['C33'].append('')
            inputs['C34'].append('')
            inputs['C35'].append('')
            inputs['C36'].append('')
            inputs['C44'].append('')
            inputs['C45'].append('')
            inputs['C46'].append('')
            inputs['C55'].append('')
            inputs['C56'].append('')
            inputs['C66'].append('')
            inputs['C_M'].append('')
            inputs['C_lambda'].append('')
            inputs['C_mu'].append('')
            inputs['C_E'].append('')
            inputs['C_nu'].append('')
            inputs['C_K'].append('')

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