#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import glob
import tempfile
import shutil

from DataModelDict import DataModelDict as DM

import iprPy

def main(*args):

    #Read in input script terms
    input_dict = __read_input_file(args[0])

    #Copy all records of a given style from one database to another
    copy(input_dict['dbase1'], input_dict['dbase2'],
         record_style = input_dict['record_style'],
         includetar = input_dict['includetar'])

def copy(dbase1, dbase2, record_style=None, includetar=True):
    """
    Copy all records of a given style from one database to another.
    
    Arguments:
    dbase1 -- iprPy.Database to copy records from
    dbase2 -- iprPy.Database to copy records to
    record_style -- style of record to copy
    """
    if record_style is None:
        #Build list of calculation records
        styles = iprPy.record_styles()
        styles.append(None)
        
        #Ask for selection
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
    
        #Retrieve records from dbase1
        records = dbase1.get_records(style=record_style)
        
        #Copy records
        for record in records:
            try: 
                dbase2.add_record(record=record)
            except: 
                pass
        
        #Copy archives
        if includetar:
            tempdir = tempfile.mkdtemp()
            for record in records:
                try: 
                    tar = dbase1.get_tar(record=record)
                except: 
                    pass
                else:
                    tar.extractall(tempdir)
                    try:
                        dbase2.add_tar(record=record, root_dir=tempdir)
                    except:
                        pass
                    shutil.rmtree(os.path.join(tempdir, record.name))
            shutil.rmtree(tempdir)
                    
                    
                    
        
    


def __read_input_file(fname):
    """Read check input file"""

    with open(fname) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    input_dict['dbase1'] = iprPy.database_fromdict(input_dict, 'database1')
    input_dict['dbase2'] = iprPy.database_fromdict(input_dict, 'database2')
    input_dict['record_style'] = input_dict.get('record_style', None)
    input_dict['includetar'] = iprPy.input.boolean(input_dict.get('includetar', True))
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])