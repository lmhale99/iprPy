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

def input(*args):
    """Main function associated with generic_input.py"""
    try:
        infile = args[0]
    except:
        raise ValueError('Input file not given')
    
    input_dict = __read_input(infile)
    
    try:
        input_dict['uuid'] = args[1]
    except:
        if 'uuid' not in input_dict:
            input_dict['uuid'] = str(uuid.uuid4())
    
    __process_input(input_dict)
    
    return input_dict           
        
def value_unit(term, default_unit=None):
    try:
        i = term.strip().index(' ')
        value = float(term[:i])
        unit = term[i+1:]
    except:
        value = float(term)
        unit = default_unit
    return uc.set_in_units(value, unit)   

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
        
        
def yield_symbols(load, load_options, load_elements, v, potential):
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
        if element in v:
            load_elements[i] = v[element]
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
    
        
def __read_input(infile):    
    """convert input file lines into a DataModelDict"""
    input_dict = {}
    for line in infile:
        terms = line.split()
        if len(terms) != 0 and terms[0][0] != '#':
            if terms[0] in input_dict:
                raise ValueError(terms[0] + ' already listed')
            if len(terms) == 1:
                pass
            else:
                input_dict[terms[0]] = ' '.join(terms[1:])
                
    return input_dict    

def __process_input(input_dict):
    """read in and process the calculation input script"""    
    
    #lammps_command
    if 'lammps_command' not in input_dict:
        raise ValueError('lammps_command not supplied')
        
    #mpi_command
    if 'mpi_command' not in input_dict:
        input_dict['mpi_command'] = None
    
    #potential_file
    if 'potential_file' in input_dict:
        with open(input_dict['potential_file']) as f:
            input_dict['potential'] = DM(f)
    else:
        raise ValueError('potential_file not supplied')        
    
    #potential_dir
    if 'potential_dir' in input_dict:
        input_dict['potential_dir'] = os.path.abspath(input_dict['potential_dir'])
    else:
        input_dict['potential_dir'] = ''
        
    #default units
    if 'length_unit' not in input_dict:
        input_dict['length_unit'] = 'angstrom'
    if 'energy_unit' not in input_dict:
        input_dict['energy_unit'] = 'eV'
    if 'pressure_unit' not in input_dict:
        input_dict['pressure_unit'] = 'GPa'
    if 'force_unit' not in input_dict:
        input_dict['force_unit'] = 'eV/angstrom'
     
    #load
    if 'load' in input_dict:
        load_style = input_dict['load'].split(' ')[0]
        load_file = ' '.join(input_dict['load'].split(' ')[1:])
    else:
        raise ValueError('load command for initial structure not supplied')
    
    if load_style == 'system_model':
        with open(load_file) as f:
            model = DM(f)
        try:
            input_dict['system_family'] = model.find('system-info')['artifact']['family']
        except:
            input_dict['system_family'] = os.path.splitext(os.path.basename(load_file))[0]
    else:
        input_dict['system_family'] = os.path.splitext(os.path.basename(load_file))[0]
    
    #load_options
    kwargs = {}
    if 'load_options' in input_dict:
        i = 0
        load_terms = input_dict['load_options'].split(' ')
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
        try:
            symbols = ucell.load(load_style, f, **kwargs)
        except:
            symbols = None
            ucell = None            
    
    #symbols
    if 'symbols' in input_dict:
        input_dict['symbols'] = input_dict['symbols'].split(' ')
    elif symbols is not None:
        input_dict['symbols'] = symbols
    else:
        raise ValueError('')
    
    #size_mults
    if 'size_mults' in input_dict:
        terms = input_dict['size_mults'].split(' ')
        if len(terms) == 3:
            input_dict['a_mult'] = int(terms[0])
            input_dict['b_mult'] = int(terms[1])
            input_dict['c_mult'] = int(terms[2])
        elif len(terms) == 6:
            input_dict['a_mult'] = (int(terms[0]), int(terms[1]))
            input_dict['b_mult'] = (int(terms[2]), int(terms[3]))
            input_dict['c_mult'] = (int(terms[4]), int(terms[5]))
        else:
            raise ValueError('Invalid size_mults command')              
    else:
            input_dict['a_mult'] = 1
            input_dict['b_mult'] = 1
            input_dict['c_mult'] = 1
    
    #ucell and initial_system if ucell was loaded
    if ucell is not None:
        input_dict['ucell'] = ucell
        
        #box_parameters
        if 'box_parameters' in input_dict:
            terms = input_dict['box_parameters'].split(' ')
            if len(terms) == 3:
                input_dict['ucell'].box_set(a = float(terms[0]), 
                                            b = float(terms[1]), 
                                            c = float(terms[2]), 
                                            scale = True) 
            elif len(terms) == 6:
                input_dict['ucell'].box_set(a = float(terms[0]), 
                                            b = float(terms[1]), 
                                            c = float(terms[2]),
                                            alpha = float(terms[3]),                                       
                                            beta =  float(terms[4]),
                                            gamma = float(terms[5]),                                        
                                            scale = True) 
            else:
                raise ValueError('Invalid box_parameters command')                      
        input_dict['initial_system'] = deepcopy(input_dict['ucell'])
        input_dict['initial_system'].supersize(input_dict['a_mult'], input_dict['b_mult'], input_dict['c_mult'])                       
        
        
        
                        
                           