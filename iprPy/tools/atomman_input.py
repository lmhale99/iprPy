#!/usr/bin/env python

#Standard library imports
import os
import sys
import uuid
from copy import deepcopy

#External packages imports
import numpy as np
from DataModelDict import DataModelDict as DM
import atomman as am
import atomman.unitconvert as uc  

def get_value(v, key, default=None):
    """
    Checks if v[key] is a singular value.  If it is, then the value is returned.
    If key is not assigned, then default is returned if it is not None.
    Other possibilities result in errors.
    """    
    
    value = v.get(key, default)
    if value is None:
        raise KeyError('Variable ' + key + ' not defined')
    elif isinstance(value, list):
        assert len(value) == 1, 'Variable ' + key + ' must have exactly one value'
        return value[0]
    else:
        return value
        
        
def yield_symbols(load, load_options, load_elements, global_variables, potential):
    """Interpret the load_elements string and yield all symbols combinations"""

    pot_symbols = np.array(potential.symbols)
    pot_elements = np.array(potential.elements())

    #if load_elements is empty, then use elements from the load file
    if load_elements == '':
        load_elements = []
        
        load_terms = load.split(' ')
        load_style = load_terms[0]
        load_file =  ' '.join(load_terms[1:])    
        
        if load_style == 'system_model':
            #system_model stores symbols
            pot_elements = pot_symbols
            
            #try searching for 'symbols'
            with open(load_file) as f:
                model = DM(f)
            load_elements = model.finds('symbols')
            
        if len(load_elements) == 0:
            #parse load_options
            kwargs= {}
            if load_options != '':
                load_options_keys = ['key', 'data_set', 'pbc', 'atom_style', 'units', 'prop_info']
                kwargs = term_extractor(load_options, {}, load_options_keys)
    
            #try loading file
            try:
                ucell = am.System()
                load_elements = ucell.load(load_style, load_file, **kwargs)
            except:
                raise ValueError('Failed to load file')
  
    else:
        assert load_elements[0] == '[' and load_elements[-1] == ']', 'Invalid symbols entry'
        load_elements = load_elements[1:-1].split(',')
  
    if load_elements[0] is None:
        #iterate over every symbols combination allowed by the potential
        for i_vals in iterbox(len(pot_elements), len(load_elements)):
            yield pot_symbols[i_vals]
                
    else:
        #Check if elements are names in global_variables
        for i in xrange(len(load_elements)):
            load_element = load_elements[i].strip()
            if load_element in global_variables:
                load_elements[i] = global_variables[load_element]
            else:
                load_elements[i] = [load_element]

        #iterate over every symbols combination allowed by the potential
        for i_vals in iterbox(len(pot_elements), len(load_elements)):
            elements = pot_elements[i_vals]

            match = True
            for j in xrange(len(elements)):
                if elements[j] not in load_elements[j]: 
                    match = False
                    break
            if match:
                yield pot_symbols[i_vals]
            
def iterbox(a, b):
    """Allows for dynamic iteration over all arrays of length b where each term is in range 0-a"""
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j    
        elif b == 1:
            yield [i]            


        
                        
                           