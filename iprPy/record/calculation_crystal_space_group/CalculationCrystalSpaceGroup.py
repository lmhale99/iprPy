# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

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
from ... import __version__ as iprPy_version
from .. import Record
from ...tools import aslist

class CalculationCrystalSpaceGroup(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-crystal-space-group'
       
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
                'script',
                
                'load_file',
                'load_options',
                
                'primitivecell',
                'idealcell',
               ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
                'symmetryprecision':1e-5,
               }
    
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
        output = DM()
        output[self.contentroot] = calc = DM()
        
        # Assign uuid
        calc['key'] = input_dict['calc_key']
        
        # Save calculation parameters
        calc['calculation'] = DM()
        calc['calculation']['iprPy-version'] = iprPy_version
        calc['calculation']['atomman-version'] = am.__version__
        
        calc['calculation']['script'] = script
        calc['calculation']['run-parameter'] = run_params = DM()
        
        run_params['symmetryprecision'] = input_dict['symmetryprecision']
        run_params['primitivecell'] = input_dict['primitivecell']
        run_params['idealcell'] = input_dict['idealcell']
        
        # Save info on system files loaded
        calc['system-info'] = DM()
        calc['system-info']['family'] = input_dict['family']
        calc['system-info']['artifact'] = DM()
        calc['system-info']['artifact']['file'] = input_dict['load_file']
        calc['system-info']['artifact']['format'] = input_dict['load_style']
        calc['system-info']['artifact']['load_options'] = input_dict['load_options']
        calc['system-info']['symbol'] = input_dict['symbols']
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            
            # Save info on initial and final configuration files
            calc['Pearson-symbol'] = results_dict['pearson']
            calc['space-group'] = DM()
            calc['space-group']['number'] = results_dict['number']
            calc['space-group']['Hermann-Maguin'] = results_dict['international']
            calc['space-group']['Schoenflies'] = results_dict['schoenflies']
            
            wykoffletters, wykoffmults = np.unique(results_dict['wyckoffs'], return_counts=True)
            for letter, mult in zip(wykoffletters, wykoffmults):
                wykoff = DM()
                wykoff['letter'] = letter
                wykoff['multiplicity'] = int(mult)
                calc['space-group'].append('Wykoff', wykoff)
            calc['space-group']['Wyckoff-fingerprint'] = results_dict['wyckoff_fingerprint']
            
            system_model = results_dict['ucell'].dump('system_model',
                                                       box_unit=input_dict['length_unit'])
            calc['unit-cell-atomic-system'] = system_model['atomic-system']
        
        self.content = output
    
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
        
        calc = self.content[self.contentroot]
        params = {}
        params['key'] = calc['key']
        params['script'] = calc['calculation']['script']
        params['iprPy_version'] = calc['calculation']['iprPy-version']
        
        params['symmetryprecision'] = calc['calculation']['run-parameter']['symmetryprecision']
        params['primitivecell'] = calc['calculation']['run-parameter']['primitivecell']
        params['idealcell'] = calc['calculation']['run-parameter']['idealcell']
        
        params['load_file'] = calc['system-info']['artifact']['file']
        params['load_style'] = calc['system-info']['artifact']['format']
        params['load_options'] = calc['system-info']['artifact']['load_options']
        params['family'] = calc['system-info']['family']
        
        symbols = aslist(calc['system-info']['symbol'])
        if flat is True:
            try:
                params['symbols'] = ' '.join(symbols)
            except:
                params['symbols'] = np.nan
        else:
            params['symbols'] = symbols
        
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
        if full is True and params['status'] == 'finished':
            ucell = am.load('system_model', self.content, key='unit-cell-atomic-system')
            params['pearson_symbol'] = calc['Pearson-symbol']
            params['spacegroup_number'] = calc['space-group']['number']
            params['spacegroup_international'] = calc['space-group']['Hermann-Maguin']
            params['spacegroup_Schoenflies'] = calc['space-group']['Schoenflies']
            params['wykoff_fingerprint'] = calc['space-group']['Wyckoff-fingerprint']
            params['composition'] = ucell.composition
            
            if flat is True:
                params['a'] = ucell.box.a
                params['b'] = ucell.box.b
                params['c'] = ucell.box.c
                params['alpha'] = ucell.box.alpha
                params['beta'] = ucell.box.beta
                params['gamma'] = ucell.box.gamma
                params['natoms'] = ucell.natoms
            else:
                params['ucell'] = ucell
        
        return params