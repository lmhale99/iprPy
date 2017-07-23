#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
import sys

import iprPy

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict)

    destroy(dbase =        input_dict['dbase'],
            record_style = input_dict['record_style'])

def destroy(dbase, record_style=None):
    """
    Permanently deletes all records of a given style.
    
    Parameters
    ----------
    dbase :  iprPy.Database
        The database to access.
    record_style : str, optional
        The record style to delete.  If not given, then the available record
        styles will be listed and the user prompted to pick one.
    """
    
    if record_style is None:
        #Build list of calculation records
        styles = iprPy.record_styles()
        
        #Ask for selection
        print('Select record_style to destroy')
        for i, style in enumerate(styles):
            print(i+1, style)
        choice = iprPy.tools.screen_input(':')
        try:
            choice = int(choice)
        except:
            record_style = choice
        else:
            record_style = styles[choice-1]
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
            
    
def process_input(input_dict):
    """
    Processes the input parameter terms.
    
    Parameters
    ----------
    input_dict : dict
        Dictionary of input parameter terms.
    """
    
    input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    
if __name__ == '__main__':
    main(*sys.argv[1:])