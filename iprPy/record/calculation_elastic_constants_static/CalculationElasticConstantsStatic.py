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

class CalculationElasticConstantsStatic(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'calculation-elastic-constants-static'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-calculation-elastic-constants-static.xsd')
    
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
               ]
    
    @property
    def compare_fterms(self):
        """
        list of str: The default fterms used by isnew() for comparisons.
        """
        return [
                'strainrange',
               ]
    
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
        
        run_params['strain-range'] = input_dict['strainrange']
        run_params['energytolerance'] = input_dict['energytolerance']
        run_params['forcetolerance'] = uc.model(input_dict['forcetolerance'], 
                                                input_dict['energy_unit'] + '/' 
                                                + input_dict['length_unit'])
        run_params['maxiterations']  = input_dict['maxiterations']
        run_params['maxevaluations'] = input_dict['maxevaluations']
        run_params['maxatommotion']  = uc.model(input_dict['maxatommotion'],
                                                input_dict['length_unit'])
        
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
        
        if results_dict is None:
            calc['status'] = 'not calculated'
        else:
            cij = DM()
            cij['Cij'] = uc.model(results_dict['raw_cij_negative'], 'GPa')
            calc.append('raw-elastic-constants', cij)
            cij['Cij'] = uc.model(results_dict['raw_cij_positive'], 'GPa')
            calc.append('raw-elastic-constants', cij)
            
            calc['elastic-constants'] = DM()
            calc['elastic-constants']['Cij'] = uc.model(results_dict['C'].Cij, 'GPa')
        
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
        
        params['strainrange'] = calc['calculation']['run-parameter']['strain-range']
        
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