#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
import os
import sys
import glob

from DataModelDict import DataModelDict as DM

import iprPy

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict)

    # Build database by adding reference records from lib_directory
    build(input_dict['dbase'], 
          lib_directory = input_dict['lib_directory'])
    
    
def build(dbase, lib_directory=None):
    """
    Adds reference records from a library to a database.
    
    Parameters
    ----------
    dbase :  iprPy.Database
        The database to access.
    lib_directory : str, optional
        The directory path for the library.  If not given, then it will use
        the iprPy/library directory.
    """

    assert dbase is not None, 'No database info supplied'

    if lib_directory is None:
        lib_directory = os.path.join(os.path.dirname(iprPy.rootdir), 'library')

    lib_directory = os.path.abspath(lib_directory)
    
    for dir in glob.iglob(os.path.join(lib_directory, '*')):

        if os.path.isdir(dir):
            record_style = os.path.basename(dir)
                            
            for record_file in glob.iglob(os.path.join(dir, '*')):
                
                if os.path.splitext(record_file)[1].lower() in ['.xml', '.json']:
                    with open(record_file) as f:
                        record = DM(f).xml()
                    record_name = os.path.splitext(os.path.basename(record_file))[0]
                    
                    try:
                        dbase.add_record(content=record, style=record_style, name=record_name)
                    except:
                        pass

                    if os.path.isdir(os.path.splitext(record_file)[0]):
                        try:
                            dbase.add_tar(root_dir=dir, name=record_name)
                        except:
                            pass
                
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
    
    input_dict['lib_directory'] = input_dict.get('lib_directory', None)
    
if __name__ == '__main__':
    main(*sys.argv[1:])