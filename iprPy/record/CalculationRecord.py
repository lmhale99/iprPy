# Standard Python libraries
from pathlib import Path
import sys

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

from . import Record
from .. import __version__ as iprPy_version

class CalculationRecord(Record):
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
        super().__init__(name=name, content=content)
        if self._mod_name == 'iprPy.record.CalculationRecord':
            raise TypeError("Don't use CalculationRecord itself, only use derived classes")
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return []
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {}
    
    def buildcontent(self, script, input_dict, results_dict=None):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        script : str
            The name of the calculation script used.
        input_dict : dict
            Dictionary of all input parameter terms.
        results_dict : dict, optional
            Dictionary containing any results produced by the calculation.
            
        Returns
        -------
        DataModelDict
            Data model consistent with the record's schema format.
        
        Raises
        ------
        AttributeError
            If buildcontent is not defined for record style.
        """
        # Create the root of the DataModelDict
        content = DM()
        content[self.contentroot] = calc = DM()
        
        # Assign uuid
        calc['key'] = input_dict['calc_key']
        
        # Save calculation parameters
        calc['calculation'] = DM()
        calc['calculation']['iprPy-version'] = iprPy_version
        calc['calculation']['atomman-version'] = am.__version__
        try:
            calc['calculation']['LAMMPS-version'] = input_dict['lammps_version']
        except:
            pass
        
        calc['calculation']['script'] = script
        calc['calculation']['branch'] = input_dict.get('branch', 'main')

        self.content = content
    
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
        
        Raises
        ------
        AttributeError
            If todict is not defined for record style.
        """
        # Fetch universal record params
        params = super().todict(full=full, flat=flat)

        # Access record's content
        calc = self.content[self.contentroot]
        
        # Set universal calculation record params
        params['iprPy_version'] = calc['calculation']['iprPy-version']
        params['atomman_version'] = calc['calculation']['atomman-version']
        try:
            params['LAMMPS_version'] = calc['calculation']['LAMMPS-version']
        except:
            pass
        params['script'] = calc['calculation']['script']
        params['branch'] = calc['calculation']['branch']

        # Fetch calculation status
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
        return params
    
    def isvalid(self):
        """
        Looks at the values of elements in the record to determine if the
        associated calculation would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        # Default Record.isvalid() returns True
        return True