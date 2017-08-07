#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
import os
import sys
import glob

import pandas as pd

import iprPy

def main(*args):
    """Main function called when script is executed directly."""
   
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict)

    check(dbase = input_dict['dbase'],
          record_style = input_dict['record_style'])

def check(dbase, record_style=None):
    """
    Counts and checks on the status of records in a database.
    
    Parameters
    ----------
    dbase :  iprPy.Database
        The database to access.
    record_style : str, optional
        The record style to check on.  If not given, then the available record
        styles will be listed and the user prompted to pick one.
    """
    if record_style is None:
        # Build list of calculation records
        styles = iprPy.record_styles()
        styles.append(None)
        
        # Ask for selection
        print('No record style given. Would you like to pick one?')
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
        
    if record_style is not None:
        # Display information about database records
        records = dbase.get_records(style=record_style)
        print('In database:')
        print(dbase)
        print('-', len(records), 'of style', record_style)
        sys.stdout.flush()
        if len(records) > 0 and 'calculation' in record_style:
            # Read records into DataFrame
            df = []
            for record in records:
                df.append(record.todict(full=False))
            df = pd.DataFrame(df)  
            
            count = len(df[df.status == 'finished'])
            print(' -', count, 'are complete')
            sys.stdout.flush()
            
            count = len(df[df.status == 'not calculated'])
            print(' -', count, 'still to run')
            sys.stdout.flush()
            
            count = len(df[df.status == 'error'])
            print(' -', count, 'issued errors')
            sys.stdout.flush()
            
            
def process_input(input_dict):
    """
    Processes the input parameter terms.
    
    Parameters
    ----------
    input_dict : dict
        Dictionary of input parameter terms.
    """
    
    if 'database' in input_dict:
        input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    else: 
        input_dict['dbase'] = None
        
    input_dict['record_style'] = input_dict.get('record_style', None)
    
if __name__ == '__main__':
    main(*sys.argv[1:])