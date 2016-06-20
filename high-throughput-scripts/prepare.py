#!/usr/bin/env python

#Standard python libraries
import os
import sys
from copy import deepcopy
import glob

#External python libraries
import iprPy
from DataModelDict import DataModelDict as DM


def main(input_file):
    """Generic method for interpreting a prepare input script"""
    model = DM()
    model['variable'] = variable = DM()
    
    #Process the lines in order
    for line in input_file:
        terms = line.split()
        
        #ignore blank and comment lines
        if len(terms) > 0 and terms[0][0] != '#':
        
            if terms[0] == 'print_check':
                print model.json(indent=2)
                
            elif terms[0] == 'calculation':
                calc_name = terms[1]
                iprPy.calculation_prepare(calc_name, terms[2:], variable)    
            
            elif terms[0] == 'list_calculations':
                for name in iprPy.calculation_names():
                    print name
            
            elif terms[0] == 'function':
                calc_name = terms[1]
                iprPy.prepare_function(calc_name, terms[2:], variable) 
            
            elif terms[0] == 'list_functions':
                for name in iprPy.prepare_function_names():
                    print name
            elif terms[0] == 'end':
                break
            
            else:
                name = terms[0]
                if len(terms) == 1:
                    raise ValueError('invalid argument "'+name+'"')
                
                elif terms[1] == 'clear':
                    del(variable[name])
                
                elif terms[1] == 'add':
                    value = ' '.join(terms[2:])
                    if value in variable:
                        value = deepcopy(variable[value])
                    if not isinstance(value, list):
                        value = [value]
                    for v in value:
                        variable.append(name, v)
                
                elif terms[1] == 'adds':
                    for value in terms[2:]:
                        if value in variable:
                            value = deepcopy(variable[value])
                        if not isinstance(value, list):
                            value = [value]
                        for v in value:
                            variable.append(name, v)
                
                else:
                    raise ValueError('invalid command: '+line)
                
if __name__ == '__main__':
    """If ran as an independent script, open the input file and pass it to main()"""
    if len(sys.argv) <= 1:
        raise IndexError('No input file specified in command line.')
    else:
        with open(' '.join(sys.argv[1:])) as f:
            main(f)
