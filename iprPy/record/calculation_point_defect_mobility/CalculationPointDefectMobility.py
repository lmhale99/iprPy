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
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from ... import __version__ as iprPy_version
from .. import Record
from ...tools import aslist

class CalculationPointDefectMobility(Record):

    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-point-defect-static'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-point-defect-static.xsd')
    
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
        return []
    
    def isvalid(self):
        """
        Looks at the values of elements in the record to determine if the
        associated calculation would be a valid one to run.
        
        Returns
        -------
        bool
            True if element combinations are valid, False if not.
        """
        #NEED TO LOOK AT THIS LATER
        #calc = self.content[self.contentroot]
        #return calc['point-defect']['system-family'] == calc['system-info']['family']
    
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
        
        run_params['box-parameters'] = DM()
        run_params['box-parameters']['a'] = list(input_dict['box_parameters'][0])
        run_params['box-parameters']['b'] = list(input_dict['box_parameters'][1])
        run_params['box-parameters']['c'] = list(input_dict['box_parameters'][2])
        
        run_params['energytolerance'] = input_dict['energytolerance']
        run_params['forcetolerance'] = uc.model(input_dict['forcetolerance'], 
                                                input_dict['energy_unit'] + '/' 
                                                + input_dict['length_unit'])
        run_params['maxatommotion']  = uc.model(input_dict['maxatommotion'],
                                                input_dict['length_unit'])
        run_params['numberreplicas'] = input_dict['numberreplicas']
        run_params['springconstant'] = input_dict['springconstant']
        run_params['thermosteps'] = input_dict['thermosteps']
        run_params['dumpsteps'] = input_dict['dumpsteps']
        run_params['minimumsteps'] = input_dict['minimumsteps']
        run_params['climbsteps'] = input_dict['climbsteps']
        run_params['timestep'] = input_dict['timestep']
        
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
        
        # Save Info on the defect parameters
        calc['point-defects'] = DM()
        calc['point-defects']['numberInitialDefects']= input_dict['initialdefect_number']
        calc['point-defects']['numberDefectPairs'] = input_dict['defect_pair_number']

        calc['point-defects']['allSymbols'] = input_dict['allSymbols']
        
        
        
        if int(calc['point-defects']['numberInitialDefects']) > 0:
            for x in range(int(calc['point-defects']['numberInitialDefects'])):
                
                pointDefectString = 'initial-point-defect-'+str(x)
                defect_type_string = 'initial_pointdefect_type_'+str(x)
                defect_atype_string = 'initial_pointdefect_atype_'+str(x)
                defect_pos_string = 'initial_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'initial_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'initial_pointdefect_scale_'+str(x)
                
                calc['point-defects'][pointDefectString]=DM()
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('initial-defect-type', 'initial-defect-atom-type', 'initial-defect-position', 'initial-defect-dumbbell-vector',
                                    'initial=defect-scale')):
                    if key1 in input_dict:
                        calc['point-defects'][pointDefectString][key2]=input_dict[key1]

        if int(calc['point-defects']['numberDefectPairs']) > 0:
            for x in range(int(calc['point-defects']['numberDefectPairs'])):
                
                pointDefectString = 'start-point-defect-'+str(x)
                defect_type_string = 'start_pointdefect_type_'+str(x)
                defect_atype_string = 'start_pointdefect_atype_'+str(x)
                defect_pos_string = 'start_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'start_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'start_pointdefect_scale_'+str(x)
                
                calc['point-defects'][pointDefectString]=DM()
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('start-defect-type', 'start-defect-atom-type', 'start-defect-position', 'start-defect-dumbbell-vector',
                                    'start=defect-scale')):
                    if key1 in input_dict:
                        calc['point-defects'][pointDefectString][key2]=input_dict[key1]

        if int(calc['point-defects']['numberDefectPairs']) > 0:
            for x in range(int(calc['point-defects']['numberDefectPairs'])):
                
                pointDefectString = 'end-point-defect-'+str(x)
                defect_type_string = 'end_pointdefect_type_'+str(x)
                defect_atype_string = 'end_pointdefect_atype_'+str(x)
                defect_pos_string = 'end_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'end_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'end_pointdefect_scale_'+str(x)
                
                calc['point-defects'][pointDefectString]=DM()
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('end-defect-type', 'end-defect-atom-type', 'end-defect-position', 'end-defect-dumbbell-vector',
                                    'end-defect-scale')):
                    if key1 in input_dict:
                        calc['point-defects'][pointDefectString][key2]=input_dict[key1]
        # Saving The Results

        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            calc['calculation']['calc-results'] = results = DM()
            results['unrelaxed'] = DM()
            results['unrelaxed']['coordinates'] = results_dict['unrelaxed_run']['coordinates']
            results['unrelaxed']['energy'] = results_dict['unrelaxed_run']['energy']
            results['minimized'] = DM()
            results['minimized']['coordinates'] = results_dict['final_minimized_run']['coordinates']
            results['minimized']['energy'] = results_dict['final_minimized_run']['energy']
            results['climbed'] = DM()
            results['climbed']['coordinates'] = results_dict['final_climb_run']['coordinates']
            results['climbed']['energy'] = results_dict['final_climb_run']['energy']
            results['minimized-and-climbed'] = DM()
            results['minimized-and-climbed']['coordinates'] = results_dict['min_and_climb_run']['coordinates']
            results['minimized-and-climbed']['energy'] = results_dict['min_and_climb_run']['energy']
            results['barrier'] = DM()
            results['barrier']['energy-units'] = results_dict['barrier']['energy_units']
            results['barrier']['forward-barrier'] = results_dict['barrier']['forward_barrier']
            results['barrier']['reverse-barrier'] = results_dict['barrier']['reverse_barrier']

        
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
        params['maxatommotion'] = calc['calculation']['run-parameter']['maxatommotion']
        params['numberreplicas'] = calc['calculation']['run-parameter']['maxatommotion']
        params['springconstant'] = calc['calculation']['run-parameter']['springconstant']
        params['thermosteps'] = calc['calculation']['run-parameter']['thermosteps']
        params['dumpsteps'] = calc['calculation']['run-parameter']['dumpsteps']
        params['minimumsteps'] = calc['calculation']['run-parameter']['minimumsteps']
        params['climbsteps'] = calc['calculation']['run-parameter']['climbsteps']
        params['timestep'] = calc['calculation']['run-parameter']['timestep']
        
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
        
        params['initial_defect_number'] = calc['point-defects']['numberInitialDefects']
        params['defectpair_number'] = calc['point-defects']['numberDefectPairs']
        params['allSymbols'] = calc['point-defects']['allSymbols']
        
        
        if int(params['initial_defect_number'])>0: #Thing here for running through all the point defects
            for x in range(int(params['pointdefect_number'])):

                calckey = 'initial-point-defect-'+str(x)
                defect_type_string = 'initial_pointdefect_type_'+str(x)
                defect_atype_string = 'initial_pointdefect_atype_'+str(x)
                defect_pos_string = 'initial_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'initial_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'initial_pointdefect_scale_'+str(x)
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('initial-defect-type', 'initial-defect-atom-type', 'initial-defect-position', 'initial-defect-dumbbell-vector',
                                    'initial-defect-scale')):
                    if key2 in calc['point-defects'][calckey]:
                        params[key1] = calc['point-defects'][calckey][key2]
                        
        if int(params['defectpair_number'])>0: #Thing here for running through all the point defects
            for x in range(int(params['defectpair_number'])):

                calckey = 'start-point-defect-'+str(x)
                defect_type_string = 'start_pointdefect_type_'+str(x)
                defect_atype_string = 'start_pointdefect_atype_'+str(x)
                defect_pos_string = 'start_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'start_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'start_pointdefect_scale_'+str(x)
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('start-defect-type', 'start-defect-atom-type', 'start-defect-position', 'start-defect-dumbbell-vector',
                                    'start-defect-scale')):
                    if key2 in calc['point-defects'][calckey]:
                        params[key1] = calc['point-defects'][calckey][key2]            

        if int(params['defectpair_number'])>0: #Thing here for running through all the point defects
            for x in range(int(params['defectpair_number'])):

                calckey = 'end-point-defect-'+str(x)
                defect_type_string = 'end_pointdefect_type_'+str(x)
                defect_atype_string = 'end_pointdefect_atype_'+str(x)
                defect_pos_string = 'end_pointdefect_pos_'+str(x)
                defect_dumbell_string = 'end_pointdefect_dumbbell_vect_'+str(x)
                defect_scale_string = 'end_pointdefect_scale_'+str(x)
                
                for key1, key2 in   zip((defect_type_string, defect_atype_string,
                                    defect_pos_string, defect_dumbell_string,
                                    defect_scale_string),('end-defect-type', 'end-defect-atom-type', 'end-defect-position', 'end-defect-dumbbell-vector',
                                    'end-defect-scale')):
                    if key2 in calc['point-defects'][calckey]:
                        params[key1] = calc['point-defects'][calckey][key2]   

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
        
        if full is True and params['status'] == 'finished': #Figuring out storing this info
        
            params['forward_barrier_energy'] = uc.value_unit(calc['barrier']['forward-barrier'])
            params['reverse_barrier_energy'] = uc.value_unit(calc['barrier']['reverse-barrier'])
            #params['natoms'] = calc['number-of-atoms']
            

            if flat is False:
                plot = calc['calculation']['calc-results']['unrelaxed']
                unrelaxed_plot = {}
                unrelaxed_plot['coordinates'] = uc.value_unit(plot['cooridnates'])
                unrelaxed_plot['energy'] = uc.value_unit(plot['energy'])
                params['unrelaxed_plot'] = pd.DataFrame(unrelaxed_plot)
                plot = calc['calculation']['calc-results']['minimized']
                minimizeded_plot = {}
                minimizeded_plot['coordinates'] = uc.value_unit(plot['cooridnates'])
                minimizeded_plot['energy'] = uc.value_unit(plot['energy'])
                params['minimizeded_plot'] = pd.DataFrame(minimizeded_plot)
                plot = calc['calculation']['calc-results']['climbed']
                climbed_plot = {}
                climbed_plot['coordinates'] = uc.value_unit(plot['cooridnates'])
                climbed_plot['energy'] = uc.value_unit(plot['energy'])
                params['climbed_plot'] = pd.DataFrame(climbed_plot)
                plot = calc['calculation']['calc-results']['minimized-and-climbed']
                min_and_climb_plot = {}
                min_and_climb_plot['coordinates'] = uc.value_unit(plot['cooridnates'])
                min_and_climb_plot['energy'] = uc.value_unit(plot['energy'])
                params['min_and_climb_plot'] = pd.DataFrame(min_and_climb_plot)
                
 
        return params
        
        