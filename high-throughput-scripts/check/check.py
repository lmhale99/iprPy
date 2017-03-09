#!/usr/bin/env python
from __future__ import print_function
import sys

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

    if 'record_style' in input_dict:
        check_record_style(input_dict['dbase'], input_dict['record_style'])
    else:
        raise ValueError('No records specified to be deleted')
    

def check_record_style(dbase, record_style):
    """Shows all of the records in dbase of style record_style"""
    records = dbase.get_records(style=record_style)
    print(len(records), 'records found. show data? (must type yes):')
    sys.stdout.flush()
    test = raw_input('')
    if test == 'yes':
        df = []
        for record in records:
            df.append(record.todict(full=False))
    df = pd.DataFrame(df)    
    print(df)
            
    
def __read_input_file(fname):
    """Read check input file"""

    with open(fname) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    input_dict['dbase'] = iprPy.database_fromdict(input_dict)
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])