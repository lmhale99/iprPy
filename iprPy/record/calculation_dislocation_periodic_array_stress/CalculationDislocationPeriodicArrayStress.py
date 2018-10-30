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

class CalculationDislocationPeriodicArrayStress(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-periodic-array-stress'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-dislocation-periodic-array-stress.xsd')
    
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

                'rigidboundaries',
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return [
                'stress_xz',
                'stress_yz',
                'temperature',
               ]
    
    def isvalid(self):
        """
        Looks at the values of elements in the record to determine if the
        associated calculation would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        return True
    
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
        
        run_params['thermosteps'] = input_dict['thermosteps']
        run_params['dumpsteps'] = input_dict['dumpsteps']
        run_params['runsteps'] = input_dict['runsteps']
        run_params['randomseed'] = input_dict['randomseed']
        
        run_params['boundarywidth'] = uc.model(input_dict['boundarywidth'], input_dict['length_unit'])
        run_params['rigidboundaries'] = input_dict['rigidboundaries']
        run_params['stress-xz'] = uc.model(input_dict['sigma_xz'], input_dict['pressure_unit'])
        run_params['stress-yz'] = uc.model(input_dict['sigma_yz'], input_dict['pressure_unit'])
        
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
        
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(input_dict['temperature'], 'K')
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            
            calc['strain-rate-relation'] = srr = DM()
            srr['time'] = uc.model(results_dict['times'], 'ns')
            srr['strain-xz'] = uc.model(results_dict['strains_xz'], None)
            srr['strain-yz'] = uc.model(results_dict['strains_yz'], None)
            
            calc['strain-rate-xz'] = uc.model(results_dict['strainrate_xz'], 's^-1')
            calc['strain-rate-yz'] = uc.model(results_dict['strainrate_yz'], 's^-1')
            
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
        params['dumpsteps'] = calc['calculation']['run-parameter']['dumpsteps']
        params['runsteps'] = calc['calculation']['run-parameter']['runsteps']
        params['randomseed'] = calc['calculation']['run-parameter']['randomseed']
        params['boundarywidth'] = uc.value_unit(calc['calculation']['run-parameter']['boundarywidth'])
        params['rigidboundaries'] = calc['calculation']['run-parameter']['rigidboundaries']
        params['stress_xz'] = uc.value_unit(calc['calculation']['run-parameter']['stress-xz'])
        params['stress_yz'] = uc.value_unit(calc['calculation']['run-parameter']['stress-yz'])
        
        params['potential_LAMMPS_key'] = calc['potential-LAMMPS']['key']
        params['potential_LAMMPS_id'] = calc['potential-LAMMPS']['id']
        params['potential_key'] = calc['potential-LAMMPS']['potential']['key']
        params['potential_id'] = calc['potential-LAMMPS']['potential']['id']
        
        params['load_file'] = calc['system-info']['artifact']['file']
        params['load_style'] = calc['system-info']['artifact']['format']
        params['load_options'] = calc['system-info']['artifact']['load_options']
        params['family'] = calc['system-info']['family']
        symbols = aslist(calc['system-info']['symbol'])
        
        params['temperature'] = uc.value_unit(calc['phase-state']['temperature'])
        
        if flat is True:
            params['symbols'] = ' '.join(symbols)
        else:
            params['symbols'] = symbols
        
        params['status'] = calc.get('status', 'finished')
        params['error'] = calc.get('error', np.nan)
        if full is True and params['status'] == 'finished':
            
            params['strainrate_xz'] = uc.value_unit(calc['strain-rate-xz'])
            params['strainrate_yz'] = uc.value_unit(calc['strain-rate-yz'])

            if flat is True:
                pass
            else:
                plot = calc['strain-rate-relation']
                sr_plot = {}
                sr_plot['t'] = uc.value_unit(plot['time'])
                sr_plot['strain_xz'] = uc.value_unit(plot['strain-xz'])
                sr_plot['strain_yz'] = uc.value_unit(plot['strain-yz'])
                params['strain_vs_time_plot'] = pd.DataFrame(sr_plot)
        
        return params