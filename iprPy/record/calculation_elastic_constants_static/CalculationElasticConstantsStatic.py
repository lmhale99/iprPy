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

class CalculationElasticConstantsStatic(CalculationRecord):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-elastic-constants-static'
    
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
        ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
            'strainrange':1e-10,
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
        
        # Copy over sizemults (rotations and shifts)
        subset('atomman_systemmanipulate').buildcontent(calc, input_dict, results_dict=results_dict)
        
        run_params['strain-range'] = input_dict['strainrange']
        # Copy over minimization parameters
        subset('lammps_minimize').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            cij = DM()
            cij['Cij'] = uc.model(results_dict['raw_cij_negative'], 'GPa')
            calc.append('raw-elastic-constants', cij)
            cij = DM()
            cij['Cij'] = uc.model(results_dict['raw_cij_positive'], 'GPa')
            calc.append('raw-elastic-constants', cij)
            
            calc['elastic-constants'] = DM()
            calc['elastic-constants']['Cij'] = uc.model(results_dict['C'].Cij, 'GPa')
    
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

        params['strainrange'] = calc['calculation']['run-parameter']['strain-range']
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        if full is True and params['status'] == 'finished':
            
            cij = uc.value_unit(calc['elastic-constants']['Cij'])
            if flat is True:
                params['C11'] = cij[0,0]
                params['C12'] = cij[0,1]
                params['C13'] = cij[0,2]
                params['C14'] = cij[0,3]
                params['C15'] = cij[0,4]
                params['C16'] = cij[0,5]
                params['C22'] = cij[1,1]
                params['C23'] = cij[1,2]
                params['C24'] = cij[1,3]
                params['C25'] = cij[1,4]
                params['C26'] = cij[1,5]
                params['C33'] = cij[2,2]
                params['C34'] = cij[2,3]
                params['C35'] = cij[2,4]
                params['C36'] = cij[2,5]
                params['C44'] = cij[3,3]
                params['C45'] = cij[3,4]
                params['C46'] = cij[3,5]
                params['C55'] = cij[4,4]
                params['C56'] = cij[4,5]
                params['C66'] = cij[5,5]
            
            else:
                params['raw_cij_negative'] = uc.value_unit(calc['raw-elastic-constants'][0]['Cij'])
                params['raw_cij_positive'] = uc.value_unit(calc['raw-elastic-constants'][1]['Cij'])
                params['C'] = am.ElasticConstants(Cij=cij)
        
        return params