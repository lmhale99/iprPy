import os
import sys
import glob
from DataModelDict import DataModelDict as DM

from iprPy.tools import term_extractor
import add_directory_files

def description():
    """Returns a description for the prepare_function."""
    return "The load_from_prototypes prepare_function adds to the 'load', 'load_options', 'load_elements', and 'box_parameters' variables using the crystal-prototype data model file(s) in 'prototype_path', and the element(s)-lattice parameter combinations listed in the reference data model file(s) 'prototype_reference'. Optional variables 'prototype_name' and 'elements' limit the addition to only the prototype names and contained elements respectively."
    
def keywords():
    """Return the list of keywords used by this prepare_function that are searched for from the inline terms and pre-defined variables."""
    return ['prototype_path', 'prototype_name']

def prepare(terms, variables):
    """
    Builds up load, load_options, elements, and box_parameters lists from 
    reference prototypes and prototype_params files.
    """
    
    assert len(variables.aslist('load')) == len(variables.aslist('load_options')),   'load and load_options must be the same length'
    assert len(variables.aslist('load')) == len(variables.aslist('load_elements')),  'load and load_elements must be the same length'
    assert len(variables.aslist('load')) == len(variables.aslist('box_parameters')), 'load and box_parameters must be the same length'
    
    v = term_extractor(terms, variables, keywords())
    
    #Generate list of files within file_directory
    add_directory_files.prepare(['file_directory', 'prototype_path', 'v_name', 'all_files'], v)
    
    #iterate through the files
    for fname in v.iteraslist('all_files'):
        proto_name, ext = os.path.splitext(os.path.basename(fname))
        
        #Check if the file is a data model
        if ext in ['.json', '.xml']:
            
            #If prototype_name is given, check that proto_name is in it
            if 'prototype_name' in v:
                if proto_name not in v.aslist('prototype_name'):
                    continue
            
            #Check that the file is a crystal-prototype data model
            try:
                with open(fname) as f:
                    proto = DM(f)
                assert 'crystal-prototype' in proto
            except:
                continue
            
            variables.append('load', 'system_model '+fname)
            variables.append('load_options', '')
            variables.append('load_elements', '')
            variables.append('box_parameters', '')