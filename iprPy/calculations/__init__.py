"""
Attributes
----------

failed_calculations : list of str
    List of all of the calculation styles that failed to load.
calculations_dict : dict
    Dictionary of the calculation styles that successfully loaded. The
    dictionary keys are the calculation style names, and the values are the
    loaded modules.
"""
# Standard Python libraries
from __future__ import division, absolute_import, print_function
import os
import importlib

__all__ = ['failed_calculations', 'calculations_dict']

failed_calculations = []

def __load_calculations():
    calculations_dict = {}
    names = []
    dir = os.path.dirname(__file__)
    ignore = ['__init__', '__pycache__']
    
    for name in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, name)):
            if name not in ignore:
                names.append(name)
            
        elif os.path.isfile(os.path.join(dir, name)):
            name, ext = os.path.splitext(name)
            
            if ext.lower() in ('.py', '.pyc'):
                if name not in ignore and name not in names:
                    names.append(name)
    
    for name in names:
        if True:
        #try:
            calculations_dict[name] = importlib.import_module('.'+name, 'iprPy.calculations')
        else:
        #except:
            failed_calculations.append(name)
    
    return calculations_dict

calculations_dict = __load_calculations()