# iprPy imports
from .. import Record

class StackingFault(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'stacking-fault'
    
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
        
        fault = self.content[self.contentroot]
        params['family'] = fault['system-family']

        calcparam = fault['calculation-parameter']
        params['a_uvw'] = calcparam['a_uvw']
        params['b_uvw'] = calcparam['b_uvw']
        params['c_uvw'] = calcparam['c_uvw']
        params['atomshift'] = calcparam['atomshift']
        params['cutboxvector'] = calcparam['cutboxvector']
        params['faultpos'] =  calcparam['faultpos']
        params['shiftvector1'] = calcparam['shiftvector1']
        params['shiftvector2'] = calcparam['shiftvector2']
        
        return params