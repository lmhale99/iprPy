#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
import glob
import os
import shutil
import tarfile 
import sys
from DataModelDict import DataModelDict as DM

import pandas as pd

import iprPy

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict)

    clean(input_dict['dbase'],
          input_dict['record_style'],
          input_dict['run_directory'])
            
def clean(dbase=None, run_directory=None, record_style=None):
    """
    Resets all records of a given style that issued errors. Useful if the
    errors are due to external conditions.
    
    Parameters
    ----------
    dbase :  iprPy.Database
        The database to access.
    run_directory : str, optional
        The directory where the cleaned calculation instances are to be
        returned.
    record_style : str, optional
        The record style to clean.  If not given, then the available record
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
        
    if dbase is not None and record_style is not None:
        # Find all records of record_style that issued errors
        records = dbase.get_records(style=record_style)
        error_df = []
        error_dict = {}
        for record in records:
            error_df.append(record.todict(full=False))
            error_dict[record.name] = record.content
        error_df = pd.DataFrame(error_df)  
        error_df = error_df[error_df.status == 'error']
        
        # Loop over all error records
        for record_name in error_df.calc_key.tolist():
            # Check if record has saved tar
            try:
                tar = dbase.get_tar(name=record_name, style=record_style)
            except:
                pass
            else:   
                # Copy tar back to run_directory
                tar.extractall(run_directory)
                tar.close()
                
                # Delete database version of tar
                try:
                    dbase.delete_tar(name=record_name, style=record_style)
                except:
                    pass
            
            # Remove error and status from stored record
            try:
                model = DM(error_dict[record_name])
            except:
                pass
            else:
                model_root = model.keys()[0]
                del(model[model_root]['error'])
                model[model_root]['status'] = 'not calculated'
                dbase.update_record(name=record_name, style=record_style, content=model.xml())
            
    
    if run_directory is not None:
        # Remove bid files
        for bidfile in glob.iglob(os.path.join(run_directory, '*', '*.bid')):
            os.remove(bidfile)
            
        # Remove results.json files
        for bidfile in glob.iglob(os.path.join(run_directory, '*', 'results.json')):
            os.remove(bidfile)
    else:
        raise ValueError('No run_directory supplied')
    
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
    
if __name__ == '__main__':
    main(*sys.argv[1:])