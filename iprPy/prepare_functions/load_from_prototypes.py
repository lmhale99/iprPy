import os
import sys
import glob
from DataModelDict import DataModelDict as DM
from iprPy.tools import atomman_input, list_build, term_extractor

def prepare(terms, v):
    """
    Builds up load, load_options, elements, and box_parameters lists from 
    reference prototypes and prototype_params files.
    """
    
    assert len(v.aslist('load')) == len(v.aslist('load_options')),   'load and load_options must be the same length'
    assert len(v.aslist('load')) == len(v.aslist('load_elements')),  'load and load_elements must be the same length'
    assert len(v.aslist('load')) == len(v.aslist('box_parameters')), 'load and box_parameters must be the same length'
    
    proto_paths = list_build(terms[0], v)
    param_paths = list_build(terms[1], v)
    
    t = term_extractor(terms[2:], ['elements', 'structures'])
    
    elements = list_build(t.aslist('elements'), v)
    structures = list_build(t.aslist('structures'), v)
    
    #Iterate over all prototype files
    for proto in proto_paths:
        proto_id = os.path.splitext(os.path.basename(proto))[0]
        
        #Skip if proto_id not in terms' structures
        if len(structures) > 0 and proto_id not in structures:
            continue
        
        #Iterate over all param files
        for param_file in param_paths:
            with open(param_file) as f:
                params = DM(f)
                
            for p_params in params.iterfinds('prototype', yes={'id':proto_id}):
                format = p_params['format']
                load_options = p_params['load_options']
                                
                for s_params in p_params.iteraslist('structure'):
                    load_elements = s_params['load_elements']
                    box_parameters = s_params['box_parameters']
                    
                    #Skip if no elements in the terms' elements
                    if len(elements) > 0:
                        match = False
                        for el in load_elements[1:-1].split(','):
                            if el.strip() in elements:
                                match = True
                                break
                        if not match:
                            continue  

                    v.append('load', format+' '+proto)
                    v.append('load_options', load_options)
                    v.append('load_elements', load_elements)
                    v.append('box_parameters', box_parameters)
            
        