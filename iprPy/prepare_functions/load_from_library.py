import os
import sys
import glob

from iprPy.tools import atomman_input, list_build, term_extractor

def prepare(terms, v):
    """
    Builds up load, load_options, elements, and box_parameter lists from 
    existing calculation records in a local directory library.
    """    
    
    assert len(v.aslist('load')) == len(v.aslist('load_options')),   'load and load_options must be the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_elements')),  'load and load_elements must be the same length'
    assert len(v.aslist('load')) == len(v.aslist('box_parameters')), 'load and box_parameters must be the same length'
    
    lib_directory = atomman_input.get_value(v, 'lib_directory')
    
    calc_name = terms[0]
    t = term_extractor(terms[1:], ['key', 'potentials', 'elements', 'structures'])
    
    key = atomman_input.get_value(v, 'key', 'relaxed-atomic-system')
    potentials = list_build(t.aslist('potentials'), v)
    elements = list_build(t.aslist('elements'), v)
    structures = list_build(t.aslist('structures'), v)

    #Iterate through list of all refine_structure results
    for fname in glob.iglob(os.path.join(lib_directory, '*', '*', '*', calc_name, '*.json')):
       
        #Check if fname already in load
        if is_path_in_list(fname, v.aslist('load')):
            continue
        
        #Extract info from file path
        calc_dir, file = os.path.split(fname)
        struct_dir, calculation = os.path.split(calc_dir)
        elem_dir, structure = os.path.split(struct_dir)
        pot_dir, element = os.path.split(elem_dir)
        potential = os.path.basename(pot_dir)
        
        #Skip if structure not in terms' structures
        if len(structures) > 0 and structure not in structures:
            continue
        
        #Skip if no elements in the terms' elements
        if len(elements) > 0:
            match = False
            for el in element.split('-'):
                if el in elements:
                    match = True
                    break
            if not match:
                continue            
            
        #skip if potential not in terms' potentials
        if len(potentials) > 0 and potential not in potentials:
            continue
        
        v.append('load', 'system_model '+fname)
        v.append('load_options', 'key ' + key)
        v.append('load_elements', '')
        v.append('box_parameters', '')
        
def is_path_in_list(path, p_list):
    for p in p_list:
        if os.path.normcase(os.path.realpath(path)) == os.path.normcase(os.path.realpath(p)):
            return True
    return False 