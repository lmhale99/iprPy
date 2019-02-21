# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys
from copy import deepcopy
from importlib import import_module

class Calculation(object):
    """
    Class for handling different calculation styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.calculations submodule.
    """
    def __init__(self):
        """
        Initializes a Calculation object for a given style.
        """
        # Get module information for current class
        self_module = sys.modules[self.__module__]
        self.__module_file = self_module.__file__
        self.__module_name = self_module.__name__
        if self.module_name == 'iprPy.calculation.Calculation':
            raise TypeError("Don't use Calculation itself, only use derived classes")
        
        # Import calculation script
        package_name = '.'.join(self.module_name.split('.')[:-1])
        self.__script = import_module('.calc_' + self.style, package_name)
        
        # Make shortcuts to calculation's functions
        self.main = self.script.main
        self.process_input = self.script.process_input
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the calculation.
        """
        return 'calculation style ' + self.style
    
    @property
    def script(self):
        return self.__script

    @property
    def module_file(self):
        return self.__module_file

    @property
    def module_name(self):
        """str: The calculation style"""
        return self.__module_name

    @property
    def style(self):
        """str: The calculation style"""
        pkgname = self.module_name.split('.')
        return pkgname[2]
    
    @property
    def directory(self):
        """str: The path to the calculation's directory"""
        return os.path.dirname(os.path.abspath(self.module_file))
    
    @property
    def record_style(self):
        """str: The record style associated with the calculation."""
        return self.script.record_style
    
    @property
    def template(self):
        """str: The template to use for generating calc.in files."""
        with open(os.path.join(self.directory,
                               'calc_' + self.style + '.template')) as template_file:
            template = template_file.read()
        
        return template
    
    def calc(self, *args, **kwargs):
        """
        Calls the calculation's primary function(s)
        """
        raise AttributeError('calc not defined for Calculation style')

    @property
    def files(self):
        """
        iter of str: Path to each file required by the calculation.
        """
        raise AttributeError('files not defined for Calculation style')
    
    @property
    def singularkeys(self):
        """list: Calculation keys that can have single values during prepare."""
        raise AttributeError('singularkeys not defined for Calculation style')
    
    @property
    def multikeys(self):
        """list: Calculation keys that can have multiple values during prepare."""
        raise AttributeError('multikeys not defined for Calculation style')
    
    @property
    def allkeys(self):
        """list: All keys used by the calculation."""
        # Build list of all keys
        allkeys = deepcopy(self.singularkeys)
        for keyset in self.multikeys:
            allkeys.extend(keyset)
        
        return allkeys