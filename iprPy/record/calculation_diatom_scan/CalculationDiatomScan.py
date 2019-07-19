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

class CalculationDiatomScan(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-diatom-scan'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            'symbols',
            'potential_LAMMPS_key',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict
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
        # Build universal content
        super().buildcontent(script, input_dict, results_dict=results_dict)
        
        # Load content after root
        calc = self.content[self.contentroot]
        
        # Assign calculation-specific run parameters
        calc['calculation']['run-parameter'] = run_params = DM()
        run_params['minimum_r'] = uc.model(input_dict['minimum_r'],
                                           input_dict['length_unit'])
        run_params['maximum_r'] = uc.model(input_dict['maximum_r'],
                                           input_dict['length_unit'])
        run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        calc['system-info'] = DM()
        calc['system-info']['symbol'] = input_dict['symbols']
        
        # Save results
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['diatom-energy-relation'] = DM()
            calc['diatom-energy-relation']['r'] = uc.model(results_dict['r_values'],
                                                             input_dict['length_unit'])
            calc['diatom-energy-relation']['potential-energy'] = uc.model(results_dict['energy_values'],
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
        
        # Extract calculation-specific run parameters
        params['minimum_r'] = uc.value_unit(calc['calculation']['run-parameter']['minimum_r'])
        params['maximum_r'] = uc.value_unit(calc['calculation']['run-parameter']['maximum_r'])
        params['number_of_steps_r'] = calc['calculation']['run-parameter']['number_of_steps_r']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)

        # Extract symbols info
        symbols = aslist(calc['system-info']['symbol'])
        if flat is True:
            params['symbols'] = ' '.join(symbols)
        else:
            params['symbols'] = symbols
        
        # Set calculation status
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
        # Extract results
        if full is True and params['status'] == 'finished':
        
            if flat is False:
                plot = calc['diatom-energy-relation']
                da_plot = {}
                da_plot['r'] = uc.value_unit(plot['r'])
                da_plot['energy'] = uc.value_unit(plot['potential-energy'])
                params['diatom_plot'] = pd.DataFrame(da_plot)
        
        return params