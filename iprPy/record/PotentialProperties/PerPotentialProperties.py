# iprPy imports
from .. import Record

class PerPotentialProperties(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'per-potential-properties'
    
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
        
        props = self.content[self.contentroot]
        params = {}
        params['potential_key'] = props['potential']['key']
        params['potential_id'] = props['potential']['id']
        params['potential_LAMMPS_key'] = props['implementation']['key']
        params['potential_LAMMPS_id'] = props['implementation']['id']
        
        params['cohesive-energy-scan'] = 'cohesive-energy-scan' in props
        params['crystal-structure'] = 'crystal-structure' in props

        return params