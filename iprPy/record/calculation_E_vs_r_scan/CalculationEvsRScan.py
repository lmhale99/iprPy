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

class CalculationEvsRScan(CalculationRecord):

    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-E-vs-r-scan'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            
            'load_file',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
            
            #'number_of_steps_r',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            #'maximum_r':0.001,
            #'minimum_r':0.001,
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
        
        # Copy over sizemults (rotations and shifts)
        subset('atomman_systemmanipulate').buildcontent(calc, input_dict, results_dict=results_dict)
        
        run_params['minimum_r'] = uc.model(input_dict['minimum_r'],
                                           input_dict['length_unit'])
        run_params['maximum_r'] = uc.model(input_dict['maximum_r'],
                                           input_dict['length_unit'])
        run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['cohesive-energy-relation'] = DM()
            calc['cohesive-energy-relation']['r'] = uc.model(results_dict['r_values'],
                                                             input_dict['length_unit'])
            calc['cohesive-energy-relation']['a'] = uc.model(results_dict['a_values'],
                                                             input_dict['length_unit'])
            calc['cohesive-energy-relation']['cohesive-energy'] = uc.model(results_dict['Ecoh_values'],
                                                                           input_dict['energy_unit'])
            
            if 'min_cell' in results_dict:
                for cell in results_dict['min_cell']:
                    system_model = cell.dump('system_model', box_unit=input_dict['length_unit'])
                    calc.append('minimum-atomic-system', system_model['atomic-system'])
    
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
        
        params['minimum_r'] = uc.value_unit(calc['calculation']['run-parameter']['minimum_r'])
        params['maximum_r'] = uc.value_unit(calc['calculation']['run-parameter']['maximum_r'])
        params['number_of_steps_r'] = calc['calculation']['run-parameter']['number_of_steps_r']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        params['number_min_states'] = len(calc.aslist('minimum-atomic-system'))
        if params['status'] == 'not calculated':
            params['number_min_states'] = 1
        
        if full is True and params['status'] == 'finished':
        
            if flat is False:
                plot = calc['cohesive-energy-relation']
                er_plot = {}
                er_plot['r'] = uc.value_unit(plot['r'])
                er_plot['a'] = uc.value_unit(plot['a'])
                er_plot['E_coh'] = uc.value_unit(plot['cohesive-energy'])
                params['e_vs_r_plot'] = pd.DataFrame(er_plot)
        
        return params