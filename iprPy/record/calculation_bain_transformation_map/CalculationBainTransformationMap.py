# coding: utf-8
raise NotImplementedError('Testing not finished')

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

class CalculationBainTransformationMap(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-bain-transformation-map'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            
            'symbol',
            
            'potential_LAMMPS_key',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            'a_bcc':1e-2,
            'a_fcc':1e-2,
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
        calc['calculation']['run-parameter'] = run_params = DM()
        
        run_params[f'size-multipliers'] = DM()
        run_params[f'size-multipliers']['a'] = list(input_dict['size_mults'][0])
        run_params[f'size-multipliers']['b'] = list(input_dict['size_mults'][1])
        run_params[f'size-multipliers']['c'] = list(input_dict['size_mults'][2])
        
        # Copy over minimization parameters
        subset('lammps_minimize').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save material/system info
        calc['system-info'] = DM()
        calc['system-info']['a_bcc'] = uc.model(input_dict['a_bcc'], 
                                                input_dict['length_unit'])
        calc['system-info']['a_fcc'] = uc.model(input_dict['a_fcc'], 
                                                input_dict['length_unit'])
        calc['system-info']['symbol'] = input_dict.get('symbol')
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['transformation-map'] = tm = DM()
            tm['a_scale'] = uc.model(results_dict['a_scale'])
            tm['c_scale'] = uc.model(results_dict['cscale'])
            
            tm['cohesive-energy'] = uc.model(results_dict['E_coh'], 
                                             input_dict['energy_unit'])

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
        
        # Extract sizemults?
        
        # Extract system info
        params['a_bcc'] = uc.value_unit(calc['system-info']['a_bcc'])
        params['a_fcc'] = uc.value_unit(calc['system-info']['a_bcc'])
        params['symbol'] = uc.value_unit(calc['system-info']['symbol'])

        
        if full is True and params['status'] == 'finished':
            
            if flat is False:
                tm = calc['transformation-map']
                params['a_scale'] = uc.value_unit(tm['a_scale'])
                params['c_scale'] = uc.value_unit(tm['c_scale'])
                params['E_coh'] = uc.value_unit(tm['E_coh'])

        return params