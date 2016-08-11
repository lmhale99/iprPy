import os
from iprPy.tools import term_extractor, atomman_input, yield_records

def description():
    """Returns a description for the prepare_function."""
    return "The load_from_library prepare_function adds to the 'load', 'load_options', 'load_elements', and 'box_parameters' variables using system_model data model file(s) in 'lib_directory' , and the element(s)-lattice parameter combinations listed in the reference data model file(s) 'prototype_reference'. Optional variables 'prototype_name' and 'elements' limit the addition to only the prototype names and contained elements respectively."
    
def keywords():
    """Return the list of keywords used by this prepare_function that are searched for from the inline terms and pre-defined variables."""
    return ['lib_directory', 
            'calc_name', 
            'load_key', 
            'potential_name', 
            'elements', 
            'system_family']

def prepare(inline_terms, global_variables):
    """
    Builds up load, load_options, elements, and box_parameter lists from 
    existing calculation records in a local directory library.
    """    

    prepare_variables = __initial_setup(inline_terms, global_variables)
     
    if prepare_variables['load_key'] == 'system-model':
        load_options = ''
    else:
        load_options = 'key ' + prepare_variables['load_key']
    
    for record_file, record in yield_records(prepare_variables['lib_directory'], 
                                             potential =     prepare_variables['potential_name'],
                                             calculation =   prepare_variables['calc_name'],
                                             elements =      prepare_variables['elements'],
                                             system_family = prepare_variables['system_family']):
        
        #Add incomplete and complete records to load with no index
        new = True
        for v_load, v_load_options in zip(global_variables.aslist('load'), global_variables.aslist('load_options')):
            v_load_file = v_load.split()[1]
            if os.path.normcase(os.path.realpath(record_file)) == os.path.normcase(os.path.realpath(v_load_file)) and load_options == v_load_options:
                new = False
                break
        if new:
            global_variables.append('load', 'system_model ' + record_file)
            global_variables.append('load_options', load_options)
            global_variables.append('load_elements', '')
            global_variables.append('box_parameters', '')   
        
        #Add records to load with indexes > 0 for complete records with multiple systems matching load_key
        for index in xrange(1, len(record.finds(prepare_variables['load_key']))):
            load_options_index = load_options + ' index ' + str(index)
  
            new = True
            for v_load, v_load_options in zip(global_variables.aslist('load'), global_variables.aslist('load_options')):
                v_load_file = v_load.split()[1]
                if os.path.normcase(os.path.realpath(record_file)) == os.path.normcase(os.path.realpath(v_load_file)) and load_options_index == v_load_options:
                    new = False
                    break
            if new:
                global_variables.append('load', 'system_model ' + record_file)
                global_variables.append('load_options', load_options_index)
                global_variables.append('load_elements', '')
                global_variables.append('box_parameters', '')
    
def __initial_setup(inline_terms, global_variables):
    """
    Builds prepare_variables from inline_terms and global_variables, and value validation.
    """    
    #Check lengths of global_variables that must be consistent
    assert len(global_variables.aslist('load')) == len(global_variables.aslist('load_options')),   'load and load_options must be of the same length'
    assert len(global_variables.aslist('load')) == len(global_variables.aslist('load_elements')),  'load and load_elements must be of the same length'
    assert len(global_variables.aslist('load')) == len(global_variables.aslist('box_parameters')), 'load and box_parameters must be of the same length'
    
    #Construct prepare_variables dictionary using_inline inline_terms and global_variables
    prepare_variables = term_extractor(inline_terms, global_variables, keywords())
    
    #Check variables that must be single valued 
    prepare_variables['lib_directory'] = atomman_input.get_value(prepare_variables, 'lib_directory')    
    prepare_variables['calc_name'] =     atomman_input.get_value(prepare_variables, 'calc_name')
    prepare_variables['load_key'] =      atomman_input.get_value(prepare_variables, 'load_key', 'system-model')       
    
    #Set default values for iterated variables
    if len(prepare_variables.aslist('potential_name')) == 0:  prepare_variables['potential_name'] = '*'  
    if len(prepare_variables.aslist('elements')) == 0:        prepare_variables['elements'] = '*'
    if len(prepare_variables.aslist('system_family')) == 0:   prepare_variables['system_family'] = '*'
        
    return prepare_variables
    
def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False   