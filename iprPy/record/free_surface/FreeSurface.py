# iprPy imports
from .. import Record

class FreeSurface(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'free-surface'
    
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

        surf = self.content[self.contentroot]
        params['family'] = surf['system-family']
        
        calcparam = surf['calculation-parameter']
        params['hkl'] = calcparam['hkl']
        params['shiftindex'] = calcparam['shiftindex']
        params['cutboxvector'] = calcparam['cutboxvector']
        
        return params