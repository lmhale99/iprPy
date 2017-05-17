#!/usr/bin/env python
from __future__ import print_function
import sys

import iprPy

def main(*args):
    """
    Main function for the destroy script. Deletes all records from a database
    of a record style.
    """
    #Read in input script terms
    input_dict = __read_input_file(args[0])

    destroy(dbase =        input_dict['dbase'], 
            record_style = input_dict['record_style'])

def destroy(dbase, record_style=None):
    """Deletes all of the records in dbase of style record_style"""
    
    if record_style is None:
        #Build list of calculation records
        styles = iprPy.record_styles()
        
        #Ask for selection
        print('Select record_style to destroy')
        for i, style in enumerate(styles):
            print(i+1, style)
        choice = iprPy.tools.screen_input(':')
        try:    choice = int(choice)
        except: record_style = choice
        else:   record_style = styles[choice-1]
        print()
    
    records = dbase.get_records(style=record_style)
    print(len(records), 'records found for', record_style)
    if len(records) > 0:
        test = iprPy.tools.screen_input('Delete records? (must type yes):')
        if test == 'yes':
            count = 0
            for record in records:
                try:
                    dbase.delete_record(record=record)
                    count += 1
                except:
                    pass
            print(count, 'records successfully deleted')
            
    
def __read_input_file(fname):
    """Read destroy input file"""

    with open(fname) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])