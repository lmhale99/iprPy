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
            record_type = os.path.basename(dir)
                            
            for record_file in glob.iglob(os.path.join(dir, '*')):
                
                if os.path.splitext(record_file)[1].lower() in ['.xml', '.json']:
                    with open(record_file) as f:
                        record = DM(f).xml()
                    record_name = os.path.splitext(os.path.basename(record_file))[0]
                    
                    try: dbase.add_record(record, record_type, record_name)
                    except: pass

                    if os.path.isdir(os.path.splitext(record_file)[0]):
                        try: dbase.add_archive(dir, record_name)
                        except: pass
                
                

def __read_input_file(fname):            
    """Read runner input file"""

    with open(fname) as f:
        build_dict = iprPy.prepare.read_variable_script(f)
    
    library_directory = os.path.abspath(build_dict.get('library_directory', 
                                        os.path.join(os.path.dirname(iprPy.rootdir), 'library')))
    dbase = iprPy.database_from_dict(build_dict)
    
    return library_directory, dbase    
    
if __name__ == '__main__':
    main(*sys.argv[1:])        