# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from .. import Record

class ReferenceCrystal(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'reference-crystal'   
    
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
        params['sourcename'] = crystal['source']['name']
        params['sourcelink'] = crystal['source']['link']
        
        ucell = am.load('system_model', self.content, key='atomic-system')
        params['composition'] = ucell.composition
        params['natypes'] = ucell.natypes
        
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