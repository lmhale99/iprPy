"""
Attributes
----------

failed_databases : list of str
    List of all of the database styles that failed to load.
databases_dict : dict
    Dictionary of the database styles that successfully loaded. The
    dictionary keys are the database style names, and the values are the
    loaded modules.
"""
from __future__ import division, absolute_import, print_function

import os
import importlib

__all__ = ['failed_databases', 'databases_dict']

failed_databases = []

def __load_databases():
    databases_dict = {}
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
            databases_dict[name] = importlib.import_module('.'+name, 'iprPy.databases')
        #else:
        except:
            failed_databases.append(name)

    return databases_dict

databases_dict = __load_databases()