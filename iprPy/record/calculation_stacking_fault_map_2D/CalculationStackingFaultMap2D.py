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

class CalculationStackingFaultMap2D(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-stacking-fault-map-2D'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-stacking-fault-map-2D.xsd')
    
    @property
    def compare_terms(self):
        """
        list of str: The default terms used by isnew() for comparisons.
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
                
                'stackingfault_key',
                
                'numshifts1',
                'numshifts2'
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return []
    
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
        
        run_params['energytolerance'] = input_dict['energytolerance']
        run_params['forcetolerance'] = uc.model(input_dict['forcetolerance'], 
                                                input_dict['energy_unit']+'/'+input_dict['length_unit'])
        run_params['maxiterations']  = input_dict['maxiterations']
        run_params['maxevaluations'] = input_dict['maxevaluations']
        run_params['maxatommotion']  = uc.model(input_dict['maxatommotion'],
                                               input_dict['length_unit'])
        
        run_params['stackingfault_numshifts1'] = input_dict['stackingfault_numshifts1']
        run_params['stackingfault_numshifts2'] = input_dict['stackingfault_numshifts2']
        
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
        
        #Save defect model information
        calc['stacking-fault'] = sf = DM()
        
        if input_dict['stackingfault_model'] is not None:
            sf['key'] = input_dict['stackingfault_model']['key']
            sf['id'] =  input_dict['stackingfault_model']['id']
        else:
            sf['key'] = None
            sf['id'] =  None
        
        sf['system-family'] = input_dict['family']
        sf['calculation-parameter'] = cp = DM()
        cp['x_axis'] = input_dict['x_axis']
        cp['y_axis'] = input_dict['y_axis']
        cp['z_axis'] = input_dict['z_axis'] 
        cp['atomshift'] = input_dict['atomshift']
        cp['cutboxvector'] = input_dict['stackingfault_cutboxvector']
        cp['faultpos'] = input_dict['stackingfault_faultpos']
        cp['shiftvector1'] = input_dict['stackingfault_shiftvector1']
        cp['shiftvector2'] = input_dict['stackingfault_shiftvector2']
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            #Save the stacking fault energy map
            calc['stacking-fault-relation'] = sfr = DM()
            sfr['shift-vector-1-fraction'] = list(results_dict['shift1'])
            sfr['shift-vector-2-fraction'] = list(results_dict['shift2'])
            sfr['energy'] = uc.model(results_dict['E_gsf'], 
                                     input_dict['energy_unit'] + '/'
                                     + input_dict['length_unit'] + '^2')
            sfr['plane-separation'] = uc.model(results_dict['delta_disp'],
                                               input_dict['length_unit'])
        
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
        
        params['energytolerance']= calc['calculation']['run-parameter']['energytolerance']
        params['forcetolerance'] = calc['calculation']['run-parameter']['forcetolerance']
        params['maxiterations'] = calc['calculation']['run-parameter']['maxiterations']
        params['maxevaluations'] = calc['calculation']['run-parameter']['maxevaluations']
        params['maxatommotion'] = calc['calculation']['run-parameter']['maxatommotion']
        
        params['numshifts1'] = calc['calculation']['run-parameter']['stackingfault_numshifts1']
        params['numshifts2'] = calc['calculation']['run-parameter']['stackingfault_numshifts2']
        
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
        
        params['stackingfault_key'] = calc['stacking-fault']['key']
        params['stackingfault_id'] = calc['stacking-fault']['id']
        
        params['shiftvector1'] = calc['stacking-fault']['calculation-parameter']['shiftvector1']
        params['shiftvector2'] = calc['stacking-fault']['calculation-parameter']['shiftvector2']
        
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
        
        if full is True:
            if params['status'] == 'error':
                params['error'] = calc['error']
            
            elif params['status'] == 'not calculated':
                pass
                
            else:
                if flat is False:
                    plot = calc['stacking-fault-relation']
                    gsf_plot = {}
                    gsf_plot['shift1'] = plot['shift-vector-1-fraction']
                    gsf_plot['shift2'] = plot['shift-vector-2-fraction']
                    gsf_plot['energy'] = uc.value_unit(plot['energy'])
                    gsf_plot['separation'] = uc.value_unit(plot['plane-separation'])
                    params['gsf_plot'] = pd.DataFrame(gsf_plot)
        
        return params