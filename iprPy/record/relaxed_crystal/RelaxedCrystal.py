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
from .. import Record
from ...tools import aslist
from ...input import subset

class RelaxedCrystal(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'relaxed-crystal'
    
    @property
    def compare_terms(self):
        """
        list: The terms to compare values absolutely.
        """
        return [
               'potential_LAMMPS_key',
               'natoms',
               'family',
               'composition',
               ]
    
    @property
    def compare_fterms(self):
        """
        dict: The terms to compare values using a tolerance.
        """
        return {
               'a':1e-6,
               'b':1e-6,
               'c':1e-6,
               'alpha':1e-2,
               'beta':1e-2,
               'gamma':1e-2,
               }
    
    def buildcontent(self, input_dict):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary of all input parameter terms.
        
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
        output[self.contentroot] = crystal = DM()
        
        # Assign uuid
        crystal['key'] = input_dict['key']
        
        # Specify source method
        crystal['method'] = input_dict['method']
        crystal['standing'] = input_dict.get('standing', 'good')
        
        # Copy over potential data model info
        subset('lammps_potential').buildcontent(crystal, input_dict)
        
        # Save info on system files loaded
        crystal['system-info'] = DM()
        crystal['system-info']['family'] = input_dict['family']
        crystal['system-info']['parent_key'] = input_dict['parent_key']
        
        system_model = input_dict['ucell'].dump('system_model',
                                                box_unit=input_dict['length_unit'])
        crystal['atomic-system'] = system_model['atomic-system']
        
        # Save cohesive energy value
        crystal['cohesive-energy'] = uc.model(input_dict['E_coh'], input_dict['energy_unit'])
        
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
        # Fetch universal record params
        params = super().todict(full=full, flat=flat)
        
        crystal = self.content[self.contentroot]
        params['method'] = crystal['method']
        params['standing'] = crystal.get('standing', 'good')
        
        # Extract potential info
        subset('lammps_potential').todict(crystal, params, full=full, flat=flat)
        
        params['family'] = crystal['system-info']['family']
        params['parent_key'] = crystal['system-info']['parent_key']
        
        ucell = am.load('system_model', self.content, key='atomic-system')
        params['composition'] = ucell.composition

        params['E_coh'] = uc.value_unit(crystal['cohesive-energy'])
        
        if flat is True:
            params['symbols'] = list(ucell.symbols)
            params['a'] = ucell.box.a
            params['b'] = ucell.box.b
            params['c'] = ucell.box.c
            params['alpha'] = ucell.box.alpha
            params['beta'] = ucell.box.beta
            params['gamma'] = ucell.box.gamma
            params['natoms'] = ucell.natoms
        else:
            params['ucell'] = ucell
        
        return params