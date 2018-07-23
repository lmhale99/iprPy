# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import uuid

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from .. import Record

class PerPotentialProperties(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'per-potential-properties'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-per-potential-properties.xsd')
    
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
        
        # Basic metadata
        props = self.content[self.contentroot]
        params = {}
        params['key'] = props['key']
        params['id'] = props['id']
        
        # E vs r scan results
        
        # Structure relaxation results
        
        # Elastic constants results
        
        return params
    
    def buildcontent(self, input_dict):
        """
        Builds a data model of the specified record style based on input (and
        results) parameters.
        
        Parameters
        ----------
        input_dict : dict
            Dictionary of input parameter terms.
        
        Returns
        -------
        DataModelDict
            Data model consistent with the record's schema format.
        """
        # Create the root of the DataModelDict
        output = DM()
        output[self.contentroot] = props = DM()
        
        # Assign uuid and id
        props['key'] = str(uuid.uuid4())
        props['id'] = 'properties.' + input_dict['potential_id']
        
        # Copy over potential data model info
        props['potential-LAMMPS'] = DM()
        props['potential-LAMMPS']['key'] = input_dict['potential_LAMMPS_key']
        props['potential-LAMMPS']['id'] = input_dict['potential_LAMMPS_id']
        props['potential-LAMMPS']['potential'] = DM()
        props['potential-LAMMPS']['potential']['key'] = input_dict['potential_key']
        props['potential-LAMMPS']['potential']['id'] = input_dict['potential_id']
        
        self.content = output