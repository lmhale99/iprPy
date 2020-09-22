# coding: utf-8
# Standard Python libraries
from pathlib import Path
import sys
from copy import deepcopy
from importlib import import_module, resources

from ..input import subset

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
        module = self.__module__

        # Throw error for default class
        if module == 'iprPy.calculation.Calculation':
            raise TypeError("Don't use Calculation itself, only use derived classes")
        
        # Extract module-based property values
        module_terms = module.split('.')
        self.__parent_module = '.'.join(module_terms[:-1])
        self.__style = module_terms[-2]

        # Import calculation script
        self.__script = import_module(f'.calc_{self.style}', self.parent_module)
        
        # Make shortcuts to calculation's functions
        self.main = self.script.main
        self.process_input = self.script.process_input
    
    def __str__(self):
        """
        str : The string representation of the calculation.
        """
        return f'calculation style {self.style}'
    
    @property
    def script(self):
        """
        module : shortcut to the imported calc_*.py module
        """
        return self.__script

    @property
    def style(self):
        """
        str: The calculation style
        """
        return self.__style
    
    @property
    def parent_module(self):
        return self.__parent_module

    @property
    def record_style(self):
        """
        str: The record style associated with the calculation.
        """
        return self.script.record_style
    
    @property
    def inputsubsets(self):
        """list: the subsets whose input key sets are used for the calculation"""
        return []

    @property
    def inputkeys(self):
        """list: the calculation-specific input keys"""
        return []

    @property
    def inputdoc(self):
        """str: the documentation for the calculation-specific input keys"""
        try:
            return resources.read_text(self.parent_module, 'runparameters.md')
        except:
            return ""

    @property
    def maindoc(self):
        """str: the overview documentation for the calculation"""
        try:
            return resources.read_text(self.parent_module, 'README.md')
        except:
            return ""

    @property
    def theorydoc(self):
        """str: the methods and theory documentation for the calculation"""
        try:
            return resources.read_text(self.parent_module, 'theory.md')
        except:
            return ""

    @property
    def template(self):
        """
        str: The template to use for generating calc.in files.
        """
        # Set the template header
        template = f'# Input script for calc_{self.style}.py\n'
        
        # Add metadata fields
        template += '\n# Calculation metadata\n'
        metakeys = ['branch']
        for key in metakeys:
            spacelen = 32 - len(key)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            template += f'{key}{space}<{key}>\n'

        # Add subset components
        for key in self.inputsubsets:
            template += subset(key).template() + '\n'
                
        # Add calculation-specific components
        if len(self.inputkeys) > 0:
            template += '\n# Run parameters\n'
            for key in self.inputkeys:
                spacelen = 32 - len(key)
                if spacelen < 1:
                    spacelen = 1
                space = ' ' * spacelen
                template += f'{key}{space}<{key}>\n'
        
        return template
    
    @property
    def templatedoc(self):
        """str: The markdown doc describing the calculation's input parameters"""
        
        # Set the documentation header
        doc = "## Input script parameters\n\n"
        doc += f"This is a list of the input parameter names recognized by calc_{self.style}.py.\n\n"

        # Describe metadata parameters
        doc += "### Global metadata parameters\n\n"
        doc += "- __branch__: assigns a group/branch descriptor to the calculation which can help with parsing results later.  Default value is 'main'.\n\n"

        # Append the subsets documentation
        for key in self.inputsubsets:
            doc += subset(key).templatedoc + '\n'

        # Append the run parameters documentation
        doc += self.inputdoc
        
        return doc

    def calc(self, *args, **kwargs):
        """
        Calls the calculation's primary function(s)
        """
        raise AttributeError('calc not defined for Calculation style')

    @property
    def files(self):
        """
        list: the names of each file required by the calculation.
        """
        # Universal files (calc_*.py)
        files = [
                    f'calc_{self.style}.py',
                ]

        return files
    
    @property
    def filedict(self):
        """dict: the names and contents of all required files."""
        filedict = {}
        for filename in self.files:
            filedict[filename] = resources.read_text(self.parent_module, filename)
        
        return filedict

    @property
    def singularkeys(self):
        """
        list: Calculation keys that can have single values during prepare.
        """
        # Universal singular keys for all calculations
        return  [
                    'branch',
                ]
    
    @property
    def multikeys(self):
        """
        list: Calculation key sets that can have multiple values during prepare.
        """
        # Universal multi key sets for all calculations
        return []
    
    @property
    def allkeys(self):
        """
        list: All keys used by the calculation.
        """
        # Build list of all keys
        allkeys = deepcopy(self.singularkeys)
        for keyset in self.multikeys:
            allkeys.extend(keyset)
        
        return allkeys