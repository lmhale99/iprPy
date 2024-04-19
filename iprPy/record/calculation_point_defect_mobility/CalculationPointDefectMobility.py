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

class CalculationPointDefectMobility(CalculationRecord):

    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-point-defect-mobility'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-point-defect-mobility.xsd')
    
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
                
                'pointdefect_mobility_key',
                
                'allSymbols'
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return {}
    
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
        return calc['point-defect-mobility']['system-family'] == calc['system-info']['family']
    
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
        
        
        # Build universal content
        super().buildcontent(script, input_dict, results_dict=results_dict)
        
        # Load content after root
        calc = self.content[self.contentroot]
        
        # Copy over sizemults (rotations and shift)
        subset('atomman_systemmanipulate').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Copy over minimization parameters
        subset('lammps_minimize').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save info on system file loaded
        subset('atomman_systemload').buildcontent(calc, input_dict, results_dict=results_dict)
        
        # Save defect model infromation
        subset('pointdefectmobility').buildcontent(calc, input_dict, results_dict = results_dict)

        #Add the below information of intererest in the lower section - need to make adjustements since this does not work normally
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['status'] = 'finished'
                                                                      
            calc['results'] = DM()
            calc['results']['forward-barrier'] = results_dict['barrier']['forward_barrier']
            calc['results']['reverse-barrier'] = results_dict['barrier']['reverse_barrier']
            calc['results']['unrelaxed-run'] = DM()
            calc['results']['unrelaxed-run']['coordinates'] = results_dict['unrelaxed_run']['coordinates']
            calc['results']['unrelaxed-run']['energy'] = results_dict['unrelaxed_run']['energy']
            calc['results']['final-minimized-run'] = DM()
            calc['results']['final-minimized-run']['coordinates'] = results_dict['final_minimized_run']['coordinates']
            calc['results']['final-minimized-run']['energy'] = results_dict['final_minimized_run']['energy']
            calc['results']['final-climbed-run'] = DM()
            calc['results']['final-climbed-run']['coordinates'] = results_dict['final_climb_run']['coordinates']
            calc['results']['final-climbed-run']['energy'] = results_dict['final_climb_run']['energy']
            calc['results']['minimized-and-climbed-combined'] = DM()
            calc['results']['minimized-and-climbed-combined']['coordinates'] = results_dict['min_and_climb_run']['coordinates']
            calc['results']['minimized-and-climbed-combined']['energy'] = results_dict['min_and_climb_run']['energy']

            
    def todict(self, full=True, flat=False):
        """
        Converts the structured content to a simpler dicitonary.
        
        Parameters
        ----------
        full : bool, optional
            Flag used by the calculation records.  A true value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True)
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparison.  If False, the terms
            values can be of any data type, which is convenient for analysis.
            (Default is False)
            
        Returns
        -------
        dict   
            A dictionary representation of the record's content.
        """
        
        #Extract universal content
        params = super().todict(full=full, flat=flat)
        calc = self.content[self.contentroot]
        
        # Extract minimization info
        subset('lammps_minimize').todict(calc, params, full=full, flat=flat)
        
        # Extract potential info
        subset('lammps_potential').todict(calc, params, full=full, flat=flat)
        
        # Extract system info
        subset('atomman_systemload').todict(calc, params, full=full, flat=flat)
        subset('atomman_systemmanipulate').todict(calc, params, full=full, flat=flat)
        
        subset('pointdefectmobility').todict(calc, params, full=full, flat=flat)
        
        
        if full is True and params['status'] == 'finished':
            #List of params
            params['forward_barrier'] = calc['results']['forward-barrier']
            params['reverse_barrier'] = calc['results']['reverse-barrier']
            params['unrelaxed_run_coordinates'] = calc['results']['unrelaxed-run']['coordinates']
            params['unrelaxed_run_energy'] = calc['results']['unrelaxed-run']['energy']
            params['final_minimized_run_coordinates'] = calc['results']['final-minimized-run']['coordinates']
            params['final_minimized_run_energy'] = calc['results']['final-minimized-run']['energy']
            params['final_climbed_run_coordinates'] = calc['results']['final-climbed-run']['coordinates']
            params['final_climbed_run_energy'] = calc['results']['final-climbed-run']['energy']
            params['min_and_climbed_coordinates'] = calc['results']['minimized-and-climbed-combined']['coordinates']
            params['min_and_climbed_energy'] = calc['results']['minimized-and-climbed-combined']['energy']
        

        return params
        
        #if full is True and params['status'] == 'finished':