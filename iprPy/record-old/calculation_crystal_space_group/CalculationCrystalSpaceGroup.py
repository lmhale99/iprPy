# coding: utf-8
# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# iprPy imports
from .. import CalculationRecord
from ...tools import aslist
from ...input import subset

class CalculationCrystalSpaceGroup(CalculationRecord):
    
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
            
            'parent_key',
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
        
        # Assign calculation-specific run parameters
        calc['calculation']['run-parameter'] = run_params = DM()
        run_params['symmetryprecision'] = input_dict['symmetryprecision']
        run_params['primitivecell'] = input_dict['primitivecell']
        run_params['idealcell'] = input_dict['idealcell']
        
        # Copy over system info data model info
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
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
        
        params['symmetryprecision'] = calc['calculation']['run-parameter']['symmetryprecision']
        params['primitivecell'] = calc['calculation']['run-parameter']['primitivecell']
        params['idealcell'] = calc['calculation']['run-parameter']['idealcell']
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        
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