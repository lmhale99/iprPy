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

class CalculationPointDefectDiffusion(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-point-defect-diffusion'

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
        dict: The terms to compare values using a tolerance.
        """
        return {
            'temperature':1,
        }
    
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
        
        run_params['thermosteps'] = input_dict['thermosteps']
        run_params['dumpsteps'] = input_dict['dumpsteps']
        run_params['runsteps'] = input_dict['runsteps']
        run_params['equilsteps'] = input_dict['equilsteps']
        run_params['randomseed'] = input_dict['randomseed']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save defined phase-state info
        calc['phase-state'] = DM()
        calc['phase-state']['temperature'] = uc.model(input_dict['temperature'], 'K')

        # Save defect model information
        subset('pointdefect').buildcontent(calc, input_dict, results_dict=results_dict)
        
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
        params['runsteps'] = calc['calculation']['run-parameter']['runsteps']
        params['randomseed'] = calc['calculation']['run-parameter']['randomseed']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        subset('pointdefect').todict(calc, params, full=full, flat=flat)
        
        params['temperature'] = uc.value_unit(calc['phase-state']['temperature'])
        
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