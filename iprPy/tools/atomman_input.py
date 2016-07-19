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
        assert len(value) == 1, 'Variable ' + key + ' must have exactly one value for ' + __calc_name__
        return value[0]
    else:
        return value
        
        
def yield_symbols(load, load_options, load_elements, variables, potential):
    """Interpret the load_elements string and yield all symbols combinations"""

    #if load_elements is empty, then use elements from the load file
    if load_elements == '':
        load_style = load.split()[0]
        load_file = ' '.join(load.split()[1:])
        load_terms = load_options.split()
        
        #system_model format stores symbols not elements
        if load_style == 'system_model':
            with open(load_file) as f:
                model = DM(f)
            symbols = model.finds('symbols')
            if len(symbols) == 0:
                kwargs = {}
                i=0
                while i < len(load_terms):
                    load_key = load_terms[i]
                    kwargs[load_key] = load_terms[i+1]
                    i += 2
                ucell = am.System()
                symbols = ucell.load(load_style, model, **kwargs)
            
            yield symbols
            raise StopIteration()
        
        kwargs = {}
        i=0
        while i < len(load_terms):
            load_key = load_terms[i]
            if load_key == 'load_prop_info':
                kwargs[load_key] = ' '.join(load_terms[i+1:])
                i = len(load_terms)
            else:
                kwargs[load_key] = load_terms[i+1]
                i += 2
        ucell = am.System()
        with open(load_file) as f:
            elements = ucell.load(load_style, f, **kwargs)  
        
        #Other formats store element names
        load_elements = '[' + ','.join(elements) + ']'
  
    #if load_elements are given, then generate possibilities from them
    assert load_elements[0] == '[' and load_elements[-1] == ']', 'Invalid symbols entry'
    load_elements = load_elements[1:-1].split(',')
    for i in xrange(len(load_elements)):
        element = load_elements[i].strip()
        if element in variables:
            load_elements[i] = variables[element]
        else:
            load_elements[i] = [element]
    #print load_elements
    pot_symbols = np.array(potential.symbols)
    pot_elements = np.array(potential.elements())
    
    #iterate over every symbols combination allowed by the potential
    for i_vals in iterbox(len(pot_elements), len(load_elements)):
        elements = pot_elements[i_vals]
        #print elements
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


        
                        
                           