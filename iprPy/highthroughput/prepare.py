#!/usr/bin/env python
from __future__ import print_function
import sys

import iprPy

def main(*args):
    """main function called when script is executed directly"""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f)
    
    # Interpret and process input parameters 
    process_input(input_dict)
    
    # Pop required terms
    dbase = input_dict.pop('dbase')
    run_directory = input_dict.pop('run_directory')
    calc_style = input_dict.pop('calculation_style')
    
    #Call prepare
    prepare(dbase, run_directory, calc_style=calc_style, input_dict=input_dict)
    
def prepare(dbase, run_directory, input_file=None, calc_style=None, input_dict=None):
    """High-throughput calculation master prepare script"""
        
    # read input_file if needed
    if input_dict is None and input_file is not None: 
        with open(input_file) as f:
            input_dict = iprPy.tools.parseinput(f)
    
    # Check for value errors
    elif input_dict is None and input_file is None: 
        raise ValueError('Either input_file or input_dict must be given')
    elif input_dict is not None and input_file is not None: 
        raise ValueError('Cannot give both input_file and input_dict')
            
    # Extract calc_style from input_dict if needed
    if calc_style is None:
        calc_style = input_dict.pop('calculation_style')
    
    # Verify singular keys are given only once
    calc = iprPy.Calculation(calc_style)
    for key in calc.prepare_keys['singular']:
        if key in input_dict and isinstance(input_dict[key], list):
            raise ValueError('Multiple terms found for singular key '+key)
    
    calc.prepare(dbase, run_directory, **input_dict)
    
def process_input(input_dict):
    """Processes the prepare_*.in input commands"""
    
    input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    input_dict['run_directory'] = os.path.abspath(input_dict['run_directory'])
        
    
if __name__ == '__main__':
    main(*sys.argv[1:])