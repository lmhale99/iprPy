# coding: utf-8
# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# iprPy imports
from .. import CalculationRecord
from ...tools import aslist
from ...input import subset

class CalculationIsolatedAtom(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-isolated-atom'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            'potential_LAMMPS_key',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict
        """
        return {}
    
    def buildcontent(self, input_dict, results_dict=None):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
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
        # Build universal content
        super().buildcontent(input_dict, results_dict=results_dict)
        
        # Load content after root
        calc = self.content[self.contentroot]
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save results
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            for symbol in results_dict['energy']:
                value = DM()
                value['symbol'] = symbol
                value['energy'] = uc.model(results_dict['energy'][symbol], input_dict['energy_unit'])
                calc.append('isolated-atom-energy', value)
    
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
        
        # Extract universal content
        params = super().todict(full=full, flat=flat)
        
        calc = self.content[self.contentroot]
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Set calculation status
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
        # Extract results
        if full is True and params['status'] == 'finished':
            
            if flat is True:
                for value in calc.aslist('isolated-atom-energy'):
                    params[value['symbol']] = uc.value_unit(value['energy'])
            if flat is False:
                params['energy'] = {}
                for value in calc.aslist('isolated-atom-energy'):
                    params['energy'][value['symbol']] = uc.value_unit(value['energy'])

        return params