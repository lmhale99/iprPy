import os
import glob

import numpy as np

from ..tools import aslist, iaslist

def get_files_in_library(lib_directory, potential=['*'], symbols=['*'], prototype=['*'], calc_type=['*'], calc_id=['*'], ext=['*']):
    """Get the file paths of all matching records"""
    
    record_paths = []
    
    for lib in iaslist(lib_directory):
        for pot in iaslist(potential):
            for sym in iaslist(symbols):
                sym = '-'.join(aslist(sym))
                for proto in iaslist(prototype):
                    for c_type in iaslist(calc_type):
                        for c_id in iaslist(calc_id):
                            for e in iaslist(ext):
                                record_paths.extend(glob.glob(os.path.join(lib_directory, pot, sym, proto, c_type, c_id+e)))
    record_paths = map(os.path.normcase, record_paths)
    return list(np.unique(record_paths))