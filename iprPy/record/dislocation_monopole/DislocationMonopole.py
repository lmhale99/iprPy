# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# iprPy imports
from .. import Record

class DislocationMonopole(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'dislocation-monopole'
    
    @property
    def schema(self):
        """
        str: The absolute directory path to the .xsd file associated with the
             record style.
        """
        return os.path.join(self.directory, 'record-dislocation-monopole.xsd')
    
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
        
        disl = self.content[self.contentroot]
        params = {}
        params['key'] = disl['key']
        params['id'] = disl['id']
        params['character'] = disl['character']
        params['burgersstring'] = disl['Burgers-vector']
        params['slipplane'] = disl['slip-plane']
        params['linedirection'] = disl['line-direction']
        params['family'] = disl['system-family']
        
        calcparam = disl['calculation-parameter']
        params['x_axis'] = calcparam['x_axis']
        params['y_axis'] = calcparam['y_axis']
        params['z_axis'] = calcparam['z_axis']
        params['atomshift'] = calcparam['atomshift']
        params['burgersvector'] = calcparam['burgersvector']
        
        return params