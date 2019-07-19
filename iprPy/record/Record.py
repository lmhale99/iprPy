# Standard Python libraries
from pathlib import Path
import sys

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

class Record(object):
    """
    Class for handling different record styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.records submodule.
    """
    
    def __init__(self, name=None, content=None):
        """
        Initializes a Record object for a given style.
        
        Parameters
        ----------
        name : str, optional
            The unique name to assign to the record.
        content : str, file-like object, DataModelDict
            The content of the record as an XML formatted str.
        """
        # Get module information for current class
        self_module = sys.modules[self.__module__]
        self._mod_file = self_module.__file__
        self._mod_name = self_module.__name__
        if self._mod_name == 'iprPy.record.Record':
            raise TypeError("Don't use Record itself, only use derived classes")
        
        self.name = name
        self.content = content
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the record.
        """
        return f'record style {self.style} named {self.name}'
    
    @property
    def style(self):
        """str: The record style"""
        pkgname = self._mod_name.split('.')
        return pkgname[2]
    
    @property
    def directory(self):
        """str: The path to the record's directory"""
        return Path(self._mod_file).resolve().parent

    @property
    def name(self):
        """str: The record's name."""
        if self.__name is not None:
            return self.__name
        else:
            raise AttributeError('name not set')
    
    @name.setter
    def name(self, value):
        if value is not None:
            self.__name = str(value)
        else:
            self.__name = None
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        raise AttributeError('contentroot not defined for Record style')
        
    @property
    def content(self):
        """
        DataModelDict: The record's content.
        """
        if self.__content is not None:
            return self.__content
        else:
            raise AttributeError('content not set')
    
    @content.setter
    def content(self, value):
        if value is not None:
            value = DM(value)
            if len(value.keys()) == 1 and self.contentroot in value:
                self.__content = DM(value)
            else:
                raise ValueError('Invalid root element for content')
        else:
            self.__content = None
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return Path(self.directory, f'record-{self.contentroot}.xsd')
    
    def todict(self, full=True, flat=False):
        """
        Converts the structured content to a simpler dictionary.
        
        Parameters
        ----------
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
            
        Returns
        -------
        dict
            A dictionary representation of the record's content.
        """
        # Universal record params
        params = {}
        params['key'] = self.content[self.contentroot]['key']
        try:
            params['id'] = self.content[self.contentroot]['id']
        except:
            pass
        
        return params
    