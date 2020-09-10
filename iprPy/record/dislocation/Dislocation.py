# iprPy imports
from .. import Record

class Dislocation(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'dislocation'
    
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

        disl = self.content[self.contentroot]
        params['character'] = disl['character']
        params['burgersvector'] = disl['Burgers-vector']
        params['slipplane'] = disl['slip-plane']
        params['linedirection'] = disl['line-direction']
        params['family'] = disl['system-family']
        
        calcparam = disl['calculation-parameter']
        params['slip_hkl'] = calcparam['slip_hkl']
        params['ξ_uvw'] = calcparam['ξ_uvw']
        params['burgers'] = calcparam['burgers']
        params['m'] = calcparam['m']
        params['n'] = calcparam['n']
        params['shift'] = calcparam.get('shift', None)
        params['shiftscale'] = calcparam.get('shiftscale', False)
        params['shiftindex'] = calcparam.get('shiftindex', None)
        
        return params