#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import glob

import pandas as pd

import iprPy

def main(*args):
    """
    Main function for the check script. Shows all matching records.
    The following check options are:
    
    - check all of a record style: provide database information and 
      'record_style', the specific style of record.
    """
    #Read in input script terms
    input_dict = __read_input_file(args[0])

    check(dbase =         input_dict['dbase'], 
          run_directory = input_dict['run_directory'], 
          record_style =  input_dict['record_style'])

def check(dbase=None, record_style=None, run_directory=None):
    
    if record_style is None:
        #Build list of calculation records
        styles = iprPy.record_styles()
        styles.append(None)
        
        #Ask for selection
        print('No record style given. Would you like to pick one?')
        for i, style in enumerate(styles):
            print(i+1, style)
        choice = iprPy.tools.screen_input(':')
        try:    choice = int(choice)
        except: record_style = choice
        else:   record_style = styles[choice-1]
        print()
        
    if run_directory is not None:
        #Display data about run_directory calculations
        count = len(glob.glob(os.path.join(run_directory, '*')))
        print('In run_directory:')
        print(run_directory)
        print('-', count, 'total calculations')
        sys.stdout.flush()
        if record_style is not None:
            count = len(glob.glob(os.path.join(run_directory, '*', 'calc_'+record_style+'.py')))
            print(' -', count, 'of style', record_style)
            sys.stdout.flush()
        print()
        
    if dbase is not None and record_style is not None:
        #Display information about database records
        records = dbase.get_records(style=record_style)
        print('In database:')
        print(dbase)
        print('-', len(records), 'of style', record_style)        
        sys.stdout.flush()
        if len(records) > 0 and 'calculation' in record_style:
            #Read records into DataFrame
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
            
            
    
def __read_input_file(fname):
    """Read check input file"""

    with open(fname) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    if 'database' in input_dict:
        input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    else: 
        input_dict['dbase'] = None
        
    input_dict['run_directory'] = input_dict.get('run_directory', None)
    input_dict['record_style'] = input_dict.get('record_style', None)
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])