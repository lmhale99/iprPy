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
        self.__mod_file = self_module.__file__
        self.__mod_name = self_module.__name__
        if self.__mod_name == 'iprPy.calculation.Calculation':
            raise TypeError("Don't use Calculation itself, only use derived classes")
        
        # Import calculation script
        module_name = '.'.join(self.__mod_name.split('.')[:-1])
        self.__calc = import_module('.calc_' + self.style, module_name)
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the calculation.
        """
        return 'calculation style ' + self.style
    
    @property
    def style(self):
        """str: The calculation style"""
        pkgname = self.__mod_name.split('.')
        return pkgname[2]
    
    @property
    def directory(self):
        """str: The path to the calculation's directory"""
        return os.path.dirname(os.path.abspath(self.__mod_file))
    
    @property
    def record_style(self):
        """str: The record style associated with the calculation."""
        return self.__calc.record_style
    
    def main(self, *args):
        """
        Calls the calculation's main function.
        """
        self.__calc.main(*args)
    
    def calc(self, *args, **kwargs):
        """
        Calls the primary calculation function(s).
        This needs to be defined for each calculation.
        """
        return None

    def process_input(self, input_dict, UUID=None, build=True):
        """
        Processes str input parameters, assigns default values if needed, and
        generates new, more complex terms as used by the calculation.
        
        Parameters
        ----------
        input_dict :  dict
            Dictionary containing the calculation input parameters with string
            values.  The allowed keys depends on the calculation style.
        UUID : str, optional
            Unique identifier to use for the calculation instance.  If not 
            given and a 'UUID' key is not in input_dict, then a random UUID4 
            hash tag will be assigned.
        build : bool, optional
            Indicates if all complex terms are to be built.  A value of False
            allows for default values to be assigned even if some inputs 
            required by the calculation are incomplete. (Default is True.)
        """
        self.__calc.process_input(input_dict, UUID=UUID, build=build)
    
    @property
    def template(self):
        """str: The template to use for generating calc.in files."""
        with open(os.path.join(self.directory,
                               'calc_' + self.style + '.template')) as template_file:
            template = template_file.read()
        
        return template
    
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