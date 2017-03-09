#!/usr/bin/env python
from __future__ import print_function
import sys

import iprPy

def main(*args):
    """
    Main function for the destroy script. Deletes records from a database.
    The following destroy options are:
    
    - destroy from list: provide database information and 'record_list', the 
      path to a file listing record names to be deleted.
    - destroy all of a record style: provide database information and 
      'record_style', the specific style of record to delete.    
    """
    #Read in input script terms
    input_dict = __read_input_file(args[0])

    if 'record_list' in input_dict:
        assert 'record_style' not in input_dict, 'record_list and record_style not simultaneously supported'
        destroy_from_list(input_dict['dbase'], input_dict['record_list'])
    elif 'record_style' in input_dict:
        destroy_record_style(input_dict['dbase'], input_dict['record_style'])
    else:
        raise ValueError('No records specified to be deleted')
    
def destroy_from_list(dbase, record_list):
    """Deletes all of the records in dbase indicated by record_list"""
    print(len(record_list), 'records to be deleted. Proceed? (must type yes):')
    sys.stdout.flush()
    test = raw_input('')
    if test == 'yes':
        count = 0
        for record in record_list:
            try:
                dbase.delete_record(name=record)
                count += 1
            except:
                pass
        print(count, 'records successfully deleted')

def destroy_record_style(dbase, record_style):
    """Deletes all of the records in dbase of style record_style"""
    records = dbase.get_records(style=record_style)
    print(len(records), 'records to be deleted. Proceed? (must type yes):')
    sys.stdout.flush()
    test = raw_input('')
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
    
    if 'record_list' in input_dict:
        with open(input_dict['record_list']) as f:
            input_dict['record_list'] = f.read().split()    
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])