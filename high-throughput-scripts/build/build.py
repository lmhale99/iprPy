#!/usr/bin/env python
import os
import sys
import glob

from DataModelDict import DataModelDict as DM

import iprPy

def main(*args):
    
    #Read in input script terms
    library_directory, dbase = __read_input_file(args[0])

    for dir in glob.iglob(os.path.join(library_directory, '*')):
        if os.path.isdir(dir):
            record_style = os.path.basename(dir)
                            
            for record_file in glob.iglob(os.path.join(dir, '*')):
                
                if os.path.splitext(record_file)[1].lower() in ['.xml', '.json']:
                    with open(record_file) as f:
                        record = DM(f).xml()
                    record_name = os.path.splitext(os.path.basename(record_file))[0]
                    
                    try: dbase.add_record(content=record, style=record_style, name=record_name)
                    except: pass

                    if os.path.isdir(os.path.splitext(record_file)[0]):
                        try: dbase.add_tar(root_dir=dir, name=record_name)
                        except: pass
                
                

def __read_input_file(fname):            
    """Read runner input file"""

    with open(fname) as f:
        build_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    library_directory = os.path.abspath(build_dict.get('library_directory', 
                                        os.path.join(os.path.dirname(iprPy.rootdir), 'library')))
    dbase = iprPy.database_fromdict(build_dict)
    
    return library_directory, dbase    
    
if __name__ == '__main__':
    main(*sys.argv[1:])        