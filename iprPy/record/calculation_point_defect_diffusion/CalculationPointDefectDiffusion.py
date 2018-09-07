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

class CalculationPointDefectDiffusion(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-point-defect-diffusion'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-point-defect-diffusion.xsd')
    
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
                
                'pointdefect_key',
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return ['temperature']
    
    def isvalid(self):
        """
        Looks at the values of elements in the record to determine if the
        associated calculation would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        calc = self.content[self.contentroot]
        return calc['point-defect']['system-family'] == calc['system-info']['family']
    
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
        
        run_params['thermosteps'] = input_dict['thermosteps']
        run_params['dumpsteps'] = input_dict['dumpsteps']
        run_params['runsteps'] = input_dict['runsteps']
        run_params['equilsteps'] = input_dict['equilsteps']
        run_params['randomseed'] = input_dict['randomseed']
        
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
        
        # Save defined phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(input_dict['temperature'], 'K')

        # Save defect parameters
        calc['point-defect'] = ptd = DM()
        if input_dict['pointdefect_model'] is not None:
            ptd['key'] = input_dict['pointdefect_model']['key']
            ptd['id'] =  input_dict['pointdefect_model']['id']
        ptd['system-family'] = input_dict.get('pointdefect_family', input_dict['family'])
        ptd['calculation-parameter'] = input_dict['calculation_params']
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            
            # Save measured phase state info
            calc['measured-phase-state'] = mps = DM()
            mps['temperature'] = uc.model(results_dict.get('temp', 0.0), 'K',
                                          results_dict.get('temp_std', None))
            mps['pressure-xx'] = uc.model(results_dict['pxx'],
                                          input_dict['pressure_unit'],
                                          results_dict['pxx_std'])
            mps['pressure-yy'] = uc.model(results_dict['pyy'],
                                          input_dict['pressure_unit'],
                                          results_dict['pyy_std'])
            mps['pressure-zz'] = uc.model(results_dict['pzz'],
                                          input_dict['pressure_unit'],
                                          results_dict['pzz_std'])
            mps['potential-energy'] = uc.model(results_dict['Epot'],
                                          input_dict['pressure_unit'],
                                          results_dict['Epot_std'])

            # Save the calculation results
            calc['diffusion-rate'] = dr = DM()
            diffusion_unit = input_dict['length_unit'] + '^2/s'
            dr['total'] = uc.model(results_dict['d'], diffusion_unit)
            dr['x-direction'] = uc.model(results_dict['dx'], diffusion_unit) 
            dr['y-direction'] = uc.model(results_dict['dy'], diffusion_unit)
            dr['z-direction'] = uc.model(results_dict['dz'], diffusion_unit)
            
            calc['number-of-atoms'] = results_dict['natoms']            
            
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
        
        params['thermosteps']= calc['calculation']['run-parameter']['thermosteps']
        params['runsteps'] = calc['calculation']['run-parameter']['runsteps']
        params['randomseed'] = calc['calculation']['run-parameter']['randomseed']
        
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
        
        params['pointdefect_key'] = calc['point-defect']['key']
        params['pointdefect_id'] = calc['point-defect']['id']
        
        params['temperature'] = uc.value_unit(calc['phase-state']['temperature'])
        
        if flat is True:
            params['a_mult1'] = sizemults['a'][0]
            params['a_mult2'] = sizemults['a'][1]
            params['b_mult1'] = sizemults['b'][0]
            params['b_mult2'] = sizemults['b'][1]
            params['c_mult1'] = sizemults['c'][0]
            params['c_mult2'] = sizemults['c'][1]
            params['symbols'] = ' '.join(symbols)
        else:
            params['sizemults'] = np.array([sizemults['a'], sizemults['b'], sizemults['c']])
            params['symbols'] = symbols
        
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        
        if full is True and params['status'] == 'finished':
        
            params['measured_temperature'] = uc.value_unit(calc['measured-phase-state']['temperature'])
            params['measured_pressure_xx'] = uc.value_unit(calc['measured-phase-state']['pressure-xx'])
            params['measured_pressure_xx_std'] = uc.error_unit(calc['measured-phase-state']['pressure-xx'])
            params['measured_pressure_yy'] = uc.value_unit(calc['measured-phase-state']['pressure-yy'])
            params['measured_pressure_yy_std'] = uc.error_unit(calc['measured-phase-state']['pressure-yy'])
            params['measured_pressure_zz'] = uc.value_unit(calc['measured-phase-state']['pressure-zz'])
            params['measured_pressure_zz_std'] = uc.error_unit(calc['measured-phase-state']['pressure-zz'])
            params['measured_potential_energy'] = uc.value_unit(calc['measured-phase-state']['potential-energy'])
            params['measured_potential_energy_std'] = uc.error_unit(calc['measured-phase-state']['potential-energy'])
            
            params['d'] = uc.value_unit(calc['diffusion-rate']['total'])
            params['dx'] = uc.value_unit(calc['diffusion-rate']['x-direction'])
            params['dy'] = uc.value_unit(calc['diffusion-rate']['y-direction'])
            params['dz'] = uc.value_unit(calc['diffusion-rate']['z-direction'])
        
            params['natoms'] = calc['number-of-atoms']

        return params