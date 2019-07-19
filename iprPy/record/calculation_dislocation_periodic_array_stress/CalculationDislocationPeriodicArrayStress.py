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

class CalculationDislocationPeriodicArrayStress(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-periodic-array-stress'
    
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
        dict: The terms to compare values using a tolerance.
        """
        return {
            'stress_xz':1e-3,
            'stress_yz':1e-3,
            'temperature':1,
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
        # Build universal content
        super().buildcontent(script, input_dict, results_dict=results_dict)

        # Load content after root
        calc = self.content[self.contentroot]
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
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
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

        params['thermosteps']= calc['calculation']['run-parameter']['thermosteps']
        params['dumpsteps'] = calc['calculation']['run-parameter']['dumpsteps']
        params['runsteps'] = calc['calculation']['run-parameter']['runsteps']
        params['randomseed'] = calc['calculation']['run-parameter']['randomseed']
        params['boundarywidth'] = uc.value_unit(calc['calculation']['run-parameter']['boundarywidth'])
        params['rigidboundaries'] = calc['calculation']['run-parameter']['rigidboundaries']
        params['stress_xz'] = uc.value_unit(calc['calculation']['run-parameter']['stress-xz'])
        params['stress_yz'] = uc.value_unit(calc['calculation']['run-parameter']['stress-yz'])
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        
        params['temperature'] = uc.value_unit(calc['phase-state']['temperature'])
        
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