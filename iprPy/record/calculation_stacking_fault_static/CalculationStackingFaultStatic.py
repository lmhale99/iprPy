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

class CalculationStackingFaultStatic(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-stacking-fault-static'

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
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            'shiftfraction1':1e-5,
            'shiftfraction2':1e-5,
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
        return calc['stacking-fault']['system-family'] == calc['system-info']['family']
    
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
        
        # Copy over minimization parameters
        subset('lammps_minimize').buildcontent(calc, input_dict, results_dict=results_dict)
        
        run_params['stackingfault_shiftfraction1'] = input_dict['stackingfault_shiftfraction1']
        run_params['stackingfault_shiftfraction2'] = input_dict['stackingfault_shiftfraction2']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save defect model information
        subset('stackingfault').buildcontent(calc, input_dict, results_dict=results_dict)
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['defect-free-system'] = DM()
            calc['defect-free-system']['artifact'] = DM()
            calc['defect-free-system']['artifact']['file'] = results_dict['dumpfile_0']
            calc['defect-free-system']['artifact']['format'] = 'atom_dump'
            calc['defect-free-system']['symbols'] = input_dict['symbols']
            calc['defect-free-system']['potential-energy'] = uc.model(results_dict['E_total_0'],
                                                                      input_dict['energy_unit'])
            
            calc['defect-system'] = DM()
            calc['defect-system']['artifact'] = DM()
            calc['defect-system']['artifact']['file'] = results_dict['dumpfile_sf']
            calc['defect-system']['artifact']['format'] = 'atom_dump'
            calc['defect-system']['symbols'] = input_dict['symbols']
            calc['defect-system']['potential-energy'] = uc.model(results_dict['E_total_sf'],
                                                                 input_dict['energy_unit'])
            
            # Save the stacking fault energy
            calc['stacking-fault-energy'] = uc.model(results_dict['E_gsf'],
                                                     input_dict['energy_unit'] + '/'
                                                     + input_dict['length_unit'] + '^2')
            
            # Save the plane separation
            calc['plane-separation'] = uc.model(results_dict['delta_disp'],
                                                input_dict['length_unit'])
    
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
        
        # Extract minimization info
        subset('lammps_minimize').todict(calc, params, full=full, flat=flat)
        
        params['shiftfraction1'] = calc['calculation']['run-parameter']['stackingfault_shiftfraction1']
        params['shiftfraction2'] = calc['calculation']['run-parameter']['stackingfault_shiftfraction2']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        subset('stackingfault').todict(calc, params, full=full, flat=flat)
        
        params['shiftvector1'] = calc['stacking-fault']['calculation-parameter']['shiftvector1']
        params['shiftvector2'] = calc['stacking-fault']['calculation-parameter']['shiftvector2']
        
        if full is True and params['status'] == 'finished':
            params['gamma_sf'] = uc.value_unit(calc['stacking-fault-energy'])
            params['delta_disp_sf'] = uc.value_unit(calc['plane-separation'])
        
        return params