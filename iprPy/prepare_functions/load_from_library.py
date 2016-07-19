import os
import sys
import glob

from iprPy.tools import term_extractor, atomman_input
import add_directory_files

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

def prepare(terms, variables):
    """
    Builds up load, load_options, elements, and box_parameter lists from 
    existing calculation records in a local directory library.
    """    
    
    assert len(variables.aslist('load')) == len(variables.aslist('load_options')),   'load and load_options must be the same length'
    assert len(variables.aslist('load')) == len(variables.aslist('load_elements')),  'load and load_elements must be the same length'
    assert len(variables.aslist('load')) == len(variables.aslist('box_parameters')), 'load and box_parameters must be the same length'
    
    v = term_extractor(terms, variables, keywords())
    
    lib_directory = v['lib_directory']
    assert not isinstance(lib_directory, list), 'lib_directory must be single-valued'
    lib_directory = os.path.abspath(lib_directory)
    assert os.path.isdir(lib_directory), 'lib_directory does not exist'
    
    assert len(v.aslist('calc_name')) > 0, 'No calc_name supplied'
    assert len(v.aslist('load_key')) <= 1, 'load_key must be single-valued if given'

    #Iterate through calc_name
    for calc_name in v.aslist('calc_name'):
        
        #Iterate over files for calc_name in lib_directory 
        for fname in glob.iglob(os.path.join(lib_directory, '*', '*', '*', calc_name, '*')):
            
            #Check that fname is a data model file
            if os.path.splitext(fname)[1].lower() not in ['.json', '.xml']:
                continue
            
            #Check if fname already in load
            if is_path_in_list(fname, variables.aslist('load')):
                continue
            
            #Extract info from file path
            calc_dir, file = os.path.split(fname)
            family_dir, calculation = os.path.split(calc_dir)
            elem_dir, system_family = os.path.split(family_dir)
            pot_dir, elements = os.path.split(elem_dir)
            potential_name = os.path.basename(pot_dir)
            
            #Check if system_family matches those specified
            if 'system_family' in v and system_family not in v.aslist('system_family'):
                continue
 
            #Check if potential_name matches those specified
            if 'potential_name' in v and potential_name not in v.aslist('potential_name'):
                continue
            
            #Check if elements in the terms' elements
            if 'elements' in v:
                match = False
                for el in elements.split('-'):
                    if el in v.aslist('elements'):
                        match = True
                        break
                if not match:
                    continue            
                
            variables.append('load', 'system_model '+fname)
            if 'load_key' in v:
                variables.append('load_options', 'key ' + v['load_key'])
            else:
                variables.append('load_options', '')
            variables.append('load_elements', '')
            variables.append('box_parameters', '')
        
def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False 