#!/usr/bin/env python
from __future__ import print_function
import sys

import iprPy

def main(*args):
    """main function called when script is executed directly"""
    
    calc_style = args[0]
    input_file = args[1]

    #open database
    dbase = iprPy.database_fromdict(input_dict)
    
    #Call prepare
    prepare(calc_style, dbase, input_dict['run_directory'], input_file=input_file)
    
def prepare(calc_style, dbase, run_directory, input_file=None, input_dict=None):
    """High-throughput calculation master prepare script"""
        
    calc = iprPy.Calculation(calc_style)
    keys = calc.prepare_keys
    
    if input_file is not None: 
        if input_dict is not None:
            raise ValueError('input_file and input_dict cannot both be given')
        else:
            with open(input_file) as f:
                input_dict = iprPy.tools.parseinput(f, singularkeys=keys['singular'])
    
    elif input_dict is None:
        raise ValueError('Either input_file or input_dict must be given')

    calc.prepare(dbase, run_directory, **input_dict)
    
if __name__ == '__main__':
    main(*sys.argv[1:])