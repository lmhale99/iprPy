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

class CalculationEvsRScan(Record):
    
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
        dict
        """
        return {
                #'maximum_r':0.001,
                #'minimum_r':0.001,
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
        calc['calculation']['LAMMPS-version'] = input_dict['lammps_version']
        
        calc['calculation']['script'] = script
        calc['calculation']['run-parameter'] = run_params = DM()
        
        run_params['size-multipliers'] = DM()
        run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
        run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
        run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
        
        run_params['minimum_r'] = uc.model(input_dict['minimum_r'],
                                           input_dict['length_unit'])
        run_params['maximum_r'] = uc.model(input_dict['maximum_r'],
                                           input_dict['length_unit'])
        run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
        
        # Copy over potential data model info
        calc['potential-LAMMPS'] = DM()
        calc['potential-LAMMPS']['key'] = input_dict['potential'].key
        calc['potential-LAMMPS']['id'] = input_dict['potential'].id
        calc['potential-LAMMPS']['potential'] = DM()
        calc['potential-LAMMPS']['potential']['key'] = input_dict['potential'].potkey
        calc['potential-LAMMPS']['potential']['id'] = input_dict['potential'].potid
        
        # Save info on system file loaded
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
        params['LAMMPS_version'] = calc['calculation']['LAMMPS-version']
        
        params['minimum_r'] = uc.value_unit(calc['calculation']['run-parameter']['minimum_r'])
        params['maximum_r'] = uc.value_unit(calc['calculation']['run-parameter']['maximum_r'])
        params['number_of_steps_r'] = calc['calculation']['run-parameter']['number_of_steps_r']
        
        sizemults = calc['calculation']['run-parameter']['size-multipliers']
        
        params['potential_LAMMPS_key'] = calc['potential-LAMMPS']['key']
        params['potential_LAMMPS_id'] = calc['potential-LAMMPS']['id']
        params['potential_key'] = calc['potential-LAMMPS']['potential']['key']
        params['potential_id'] = calc['potential-LAMMPS']['potential']['id']
        
        params['load_file'] = calc['system-info']['artifact']['file']
        params['load_style'] = calc['system-info']['artifact']['format']
        params['load_options'] = calc['system-info']['artifact']['load_options']
        params['family'] = calc['system-info']['family']
        symbols = aslist(calc['system-info']['symbol'])
        
        if flat is True:
            params['a_mult1'] = sizemults['a'][0]
            params['a_mult2'] = sizemults['a'][1]
            params['b_mult1'] = sizemults['b'][0]
            params['b_mult2'] = sizemults['b'][1]
            params['c_mult1'] = sizemults['c'][0]
            params['c_mult2'] = sizemults['c'][1]
            params['symbols'] = ' '.join(symbols)
        else:
            params['sizemults'] = np.array([sizemults['a'], sizemults['b'],
                                            sizemults['c']])
            params['symbols'] = symbols
        
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
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