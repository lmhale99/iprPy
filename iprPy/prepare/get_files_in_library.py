import os
import glob

import numpy as np

from ..tools import as_list, iter_as_list

def get_files_in_library(lib_directory, potential=['*'], symbols=['*'], prototype=['*'], calc_type=['*'], calc_id=['*'], ext=['*']):
    """Get the file paths of all matching records"""
    
    record_paths = []
    
    for lib in iter_as_list(lib_directory):
        for pot in iter_as_list(potential):
            for sym in iter_as_list(symbols):
                sym = '-'.join(as_list(sym))
                for proto in iter_as_list(prototype):
                    for c_type in iter_as_list(calc_type):
                        for c_id in iter_as_list(calc_id):
                            for e in iter_as_list(ext):
                                record_paths.extend(glob.glob(os.path.join(lib_directory, pot, sym, proto, c_type, c_id+e)))
    record_paths = map(os.path.normcase, record_paths)
    return list(np.unique(record_paths))