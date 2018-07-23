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

class CalculationDislocationMonopole(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-dislocation-monopole'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-dislocation-monopole.xsd')
    
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
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return [
                'annealtemperature',
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
        calc = self.content[self.contentroot]
        return calc['dislocation-monopole']['system-family'] == calc['system-info']['family']
    
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
        
        run_params['energytolerance'] = input_dict['energytolerance']
        run_params['forcetolerance'] = uc.model(input_dict['forcetolerance'], 
                                                input_dict['energy_unit'] + '/' 
                                                + input_dict['length_unit'])
        run_params['maxiterations']  = input_dict['maxiterations']
        run_params['maxevaluations'] = input_dict['maxevaluations']
        run_params['maxatommotion']  = uc.model(input_dict['maxatommotion'],
                                                input_dict['length_unit'])
        
        run_params['dislocation_boundarywidth'] = input_dict['boundarywidth']
        run_params['dislocation_boundaryshape'] = input_dict['boundaryshape']
        
        run_params['annealtemperature'] = input_dict['annealtemperature']
        
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
        
        #Save defect parameters
        calc['dislocation-monopole'] = disl = DM()
        if input_dict['dislocation_model'] is not None:
            disl['key'] = input_dict['dislocation_model']['key']
            disl['id'] = input_dict['dislocation_model']['id']
            disl['character'] = input_dict['dislocation_model']['character']
            disl['Burgers-vector'] = input_dict['dislocation_model']['Burgers-vector']
            disl['slip-plane'] = input_dict['dislocation_model']['slip-plane']
            disl['line-direction'] = input_dict['dislocation_model']['line-direction']
        
        disl['system-family'] = input_dict.get('dislocation_family', input_dict['family'])
        disl['calculation-parameter'] = cp = DM() 
        cp['stroh_m'] = input_dict['dislocation_stroh_m']
        cp['stroh_n'] = input_dict['dislocation_stroh_n']
        cp['a_uvw'] = input_dict['a_uvw']
        cp['b_uvw'] = input_dict['b_uvw']
        cp['c_uvw'] = input_dict['c_uvw'] 
        cp['atomshift'] = input_dict['atomshift']
        cp['burgersvector'] = input_dict['dislocation_burgersvector']
        
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
            
            calc['Stroh-pre-ln-factor'] = uc.model(results_dict['Stroh_preln'],
                                                   input_dict['energy_unit'] + '/'
                                                   + input_dict['length_unit'])
            
            calc['Stroh-K-tensor'] = uc.model(results_dict['Stroh_K_tensor'],
                                              input_dict['pressure_unit'])
            
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
        params['maxiterations'] = calc['calculation']['run-parameter']['maxiterations']
        params['maxevaluations'] = calc['calculation']['run-parameter']['maxevaluations']
        params['maxatommotion'] = calc['calculation']['run-parameter']['maxatommotion']
        
        params['annealtemperature'] = calc['calculation']['run-parameter']['annealtemperature']

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
        
        params['dislocation_key'] = calc['dislocation-monopole']['key']
        params['dislocation_id'] = calc['dislocation-monopole']['id']
        
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
        K_tensor = uc.value_unit(calc['Stroh-K-tensor'])
        if full is True and params['status'] == 'finished':
            params['preln'] = uc.value_unit(calc['Stroh-pre-ln-factor'])
            
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