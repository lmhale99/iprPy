"""
Attributes
----------

failed_records : list of str
    List of all of the record styles that failed to load.
records_dict : dict
    Dictionary of the record styles that successfully loaded. The
    dictionary keys are the record style names, and the values are the
    loaded modules.
"""
from __future__ import division, absolute_import, print_function

import os
import importlib

__all__ = ['failed_records', 'records_dict']

failed_records = []

def __load_records():
    records_dict = {}
    names = []
    dir = os.path.dirname(__file__)

    for name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, name)):
            names.append(name)
            
        elif os.path.isfile(os.path.join(dir, name)):
            name, ext = os.path.splitext(name)
            
            if ext.lower() in ('.py', '.pyc') and name != '__init__' and name not in names:
                names.append(name)
        
    for name in names:
        #if True:
        try:
            records_dict[name] = importlib.import_module('.'+name, 'iprPy.records')
        #else:
        except:
            failed_records.append(name)

    return records_dict
    
records_dict = __load_records()