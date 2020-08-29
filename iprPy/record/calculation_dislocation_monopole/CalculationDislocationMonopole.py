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

class CalculationDislocationMonopole(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-monopole'

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
            
            'a_mult1',
            'a_mult2',
            'b_mult1',
            'b_mult2',
            'c_mult1',
            'c_mult2',
            
            'dislocation_key',

            'annealsteps',
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            'annealtemperature':1,
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
        return calc['dislocation']['system-family'] == calc['system-info']['family']
    
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
        
        # Copy over minimization parameters
        subset('lammps_minimize').buildcontent(calc, input_dict, results_dict=results_dict)
        
        run_params['dislocation_boundarywidth'] = input_dict['dislocation_boundarywidth']
        run_params['dislocation_boundaryshape'] = input_dict['dislocation_boundaryshape']
        run_params['dislocation_boundaryscale'] = input_dict['dislocation_boundaryscale']
        
        run_params['annealtemperature'] = input_dict['annealtemperature']
        run_params['annealsteps'] = input_dict['annealsteps']
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save defect parameters
        subset('dislocation').buildcontent(calc, input_dict, results_dict=results_dict)
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            c_model = input_dict['C'].model(unit=input_dict['pressure_unit'])
            calc['elastic-constants'] = c_model['elastic-constants']
            
            calc['base-system'] = DM()
            calc['base-system']['artifact'] = DM()
            calc['base-system']['artifact']['file'] = results_dict['dumpfile_base']
            calc['base-system']['artifact']['format'] = 'atom_dump'
            calc['base-system']['symbols'] = results_dict['symbols_base']
            
            calc['defect-system'] = DM()
            calc['defect-system']['artifact'] = DM()
            calc['defect-system']['artifact']['file'] = results_dict['dumpfile_disl']
            calc['defect-system']['artifact']['format'] = 'atom_dump'
            calc['defect-system']['symbols'] = results_dict['symbols_disl']
            calc['defect-system']['potential-energy'] = uc.model(results_dict['E_total_disl'], 
                                                                 input_dict['energy_unit'])
            
            calc['elastic-solution'] = elsol = DM()
            elsol['pre-ln-factor'] = uc.model(results_dict['dislocation'].dislsol.preln,
                                             f"{input_dict['energy_unit']}/{input_dict['length_unit']}")
            
            elsol['K-tensor'] = uc.model(results_dict['dislocation'].dislsol.K_tensor,
                                         input_dict['pressure_unit'])
    
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
        
        params['annealtemperature'] = calc['calculation']['run-parameter']['annealtemperature']
        params['annealsteps'] = calc['calculation']['run-parameter']['annealsteps']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        
        subset('dislocation').todict(calc, params, full=full, flat=flat)
        
        if full is True and params['status'] == 'finished':
            params['preln'] = uc.value_unit(calc['elastic-solution']['pre-ln-factor'])
            K_tensor = uc.value_unit(calc['elastic-solution']['K-tensor'])

            if flat is True:
                for C in calc['elastic-constants'].aslist('C'):
                    params['C'+str(C['ij'][0])+str(C['ij'][2])] = uc.value_unit(C['stiffness'])
                params['K11'] = K_tensor[0,0]
                params['K12'] = K_tensor[0,1]
                params['K13'] = K_tensor[0,2]
                params['K22'] = K_tensor[1,1]
                params['K23'] = K_tensor[1,2]
                params['K33'] = K_tensor[2,2]
            else:
                try:
                    params['C'] = am.ElasticConstants(model=calc)
                except:
                    params['C'] = 'Invalid'
                params['K_tensor'] = K_tensor
        
        return params