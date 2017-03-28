#!/usr/bin/env python
import glob
import os
import shutil
import tarfile 
import sys
from DataModelDict import DataModelDict as DM

def main(*args):
    """
    Main function for the clean script.  
    """
    #Read in input script terms
    input_dict = __read_input_file(args[0])

    clean(input_dict['run_directory'])
            
def clean(run_directory):

    for bidfile in glob.iglob(os.path.join(run_directory, '*', '*.bid')):
        os.remove(bidfile)
    
def __read_input_file(fname):
    """Read clean input file"""

    with open(fname) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    return input_dict
    
if __name__ == '__main__':
    main(*sys.argv[1:])
