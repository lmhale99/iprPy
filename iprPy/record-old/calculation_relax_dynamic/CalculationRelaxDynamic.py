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

class CalculationRelaxDynamic(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-relax-dynamic'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
            'script',
            
            'parent_key',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            'temperature':1e-2,
            'pressure_xx':1e-2,
            'pressure_yy':1e-2,
            'pressure_zz':1e-2,
            'pressure_xy':1e-2,
            'pressure_xz':1e-2,
            'pressure_yz':1e-2,
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
        
        run_params['integrator'] = input_dict['integrator']
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
        calc['phase-state']['pressure-xx'] = uc.model(input_dict['pressure_xx'],
                                                      input_dict['pressure_unit'])
        calc['phase-state']['pressure-yy'] = uc.model(input_dict['pressure_yy'],
                                                      input_dict['pressure_unit'])
        calc['phase-state']['pressure-zz'] = uc.model(input_dict['pressure_zz'],
                                                      input_dict['pressure_unit'])
        calc['phase-state']['pressure-xy'] = uc.model(input_dict['pressure_xy'],
                                                      input_dict['pressure_unit'])
        calc['phase-state']['pressure-xz'] = uc.model(input_dict['pressure_xz'],
                                                      input_dict['pressure_unit'])
        calc['phase-state']['pressure-yz'] = uc.model(input_dict['pressure_yz'],
                                                      input_dict['pressure_unit'])
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            # Save info on initial and final configuration files
            calc['initial-system'] = DM()
            calc['initial-system']['artifact'] = DM()
            calc['initial-system']['artifact']['file'] = results_dict['dumpfile_initial']
            calc['initial-system']['artifact']['format'] = 'atom_dump'
            calc['initial-system']['symbols'] = results_dict['symbols_initial']
            
            calc['final-system'] = DM()
            calc['final-system']['artifact'] = DM()
            calc['final-system']['artifact']['file'] = results_dict['dumpfile_final']
            calc['final-system']['artifact']['format'] = 'atom_dump'
            calc['final-system']['symbols'] = results_dict['symbols_final']
            
            calc['number-of-measurements'] = results_dict.get('nsamples', 1)
            
            # Save measured box parameter info
            calc['measured-box-parameter'] = mbp = DM()
            lx = results_dict['lx'] / (input_dict['sizemults'][0][1] - input_dict['sizemults'][0][0])
            lx_std = results_dict['lx_std'] / (input_dict['sizemults'][0][1] - input_dict['sizemults'][0][0])
            ly = results_dict['ly'] / (input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0])
            ly_std = results_dict['ly_std'] / (input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0])
            lz = results_dict['lz'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            lz_std = results_dict['lz_std'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            xy = results_dict['xy'] / (input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0])
            xy_std = results_dict['xy_std'] / (input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0])
            xz = results_dict['xz'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            xz_std = results_dict['xz_std'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            yz = results_dict['yz'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            yz_std = results_dict['yz_std'] / (input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0])
            
            mbp['lx'] = uc.model(lx, input_dict['length_unit'], lx_std)
            mbp['ly'] = uc.model(ly, input_dict['length_unit'], ly_std)
            mbp['lz'] = uc.model(lz, input_dict['length_unit'], lz_std)
            mbp['xy'] = uc.model(xy, input_dict['length_unit'], xy_std)
            mbp['xz'] = uc.model(xz, input_dict['length_unit'], xz_std)
            mbp['yz'] = uc.model(yz, input_dict['length_unit'], yz_std)
            
            # Save measured phase state info
            calc['measured-phase-state'] = mps = DM()
            mps['temperature'] = uc.model(results_dict.get('temp', 0.0), 'K',
                                          results_dict.get('temp_std', None))
            mps['pressure-xx'] = uc.model(results_dict['measured_pxx'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pxx_std'])
            mps['pressure-yy'] = uc.model(results_dict['measured_pyy'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pyy_std'])
            mps['pressure-zz'] = uc.model(results_dict['measured_pzz'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pzz_std'])
            mps['pressure-xy'] = uc.model(results_dict['measured_pxy'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pxy_std'])
            mps['pressure-xz'] = uc.model(results_dict['measured_pxz'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pxz_std'])
            mps['pressure-yz'] = uc.model(results_dict['measured_pyz'],
                                          input_dict['pressure_unit'],
                                          results_dict['measured_pyz_std'])
            
            # Save the final cohesive and total energies
            calc['cohesive-energy'] = uc.model(results_dict['E_coh'],
                                               input_dict['energy_unit'],
                                               results_dict.get('E_coh_std', None))
            if 'E_total' in results_dict:
                calc['average-total-energy'] = uc.model(results_dict['E_total'],
                                                input_dict['energy_unit'],
                                                results_dict.get('E_total_std', None))
    
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
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        params['temperature'] = uc.value_unit(calc['phase-state']['temperature'])
        params['pressure_xx'] = uc.value_unit(calc['phase-state']['pressure-xx'])
        params['pressure_yy'] = uc.value_unit(calc['phase-state']['pressure-yy'])
        params['pressure_zz'] = uc.value_unit(calc['phase-state']['pressure-zz'])
        params['pressure_xy'] = uc.value_unit(calc['phase-state']['pressure-xy'])
        params['pressure_xz'] = uc.value_unit(calc['phase-state']['pressure-xz'])
        params['pressure_yz'] = uc.value_unit(calc['phase-state']['pressure-yz'])
        
        if full is True and params['status'] == 'finished':
            
            params['lx'] = uc.value_unit(calc['measured-box-parameter']['lx'])
            params['lx_std'] = uc.error_unit(calc['measured-box-parameter']['lx'])
            params['ly'] = uc.value_unit(calc['measured-box-parameter']['ly'])
            params['ly_std'] = uc.error_unit(calc['measured-box-parameter']['ly'])
            params['lz'] = uc.value_unit(calc['measured-box-parameter']['lz'])
            params['lz_std'] = uc.error_unit(calc['measured-box-parameter']['lz'])
            params['xy'] = uc.value_unit(calc['measured-box-parameter']['xy'])
            params['xy_std'] = uc.error_unit(calc['measured-box-parameter']['xy'])
            params['xz'] = uc.value_unit(calc['measured-box-parameter']['xz'])
            params['xz_std'] = uc.error_unit(calc['measured-box-parameter']['xz'])
            params['yz'] = uc.value_unit(calc['measured-box-parameter']['yz'])
            params['yz_std'] = uc.error_unit(calc['measured-box-parameter']['yz'])
            
            params['E_cohesive'] = uc.value_unit(calc['cohesive-energy'])
            params['E_cohesive_std'] = uc.error_unit(calc['cohesive-energy'])
            if 'average-total-energy' in calc:
                params['E_total_ave'] = uc.value_unit(calc['average-total-energy'])
                params['E_total_std'] = uc.error_unit(calc['average-total-energy'])

            params['measured_temperature'] = uc.value_unit(calc['measured-phase-state']['temperature'])
            params['measured_pressure_xx'] = uc.value_unit(calc['measured-phase-state']['pressure-xx'])
            params['measured_pressure_xx_std'] = uc.error_unit(calc['measured-phase-state']['pressure-xx'])
            params['measured_pressure_yy'] = uc.value_unit(calc['measured-phase-state']['pressure-yy'])
            params['measured_pressure_yy_std'] = uc.error_unit(calc['measured-phase-state']['pressure-yy'])
            params['measured_pressure_zz'] = uc.value_unit(calc['measured-phase-state']['pressure-zz'])
            params['measured_pressure_zz_std'] = uc.error_unit(calc['measured-phase-state']['pressure-zz'])
            params['measured_pressure_xy'] = uc.value_unit(calc['measured-phase-state']['pressure-xy'])
            params['measured_pressure_xy_std'] = uc.error_unit(calc['measured-phase-state']['pressure-xy'])
            params['measured_pressure_xz'] = uc.value_unit(calc['measured-phase-state']['pressure-xz'])
            params['measured_pressure_xz_std'] = uc.error_unit(calc['measured-phase-state']['pressure-xz'])
            params['measured_pressure_yz'] = uc.value_unit(calc['measured-phase-state']['pressure-yz'])
            params['measured_pressure_xyz_std'] = uc.error_unit(calc['measured-phase-state']['pressure-yz'])
        
        return params