# http://www.numpy.org/
import numpy as np

# iprPy imports
from .. import Record

class PotentialLAMMPS(Record):
    
    @property
    def contentroot(self):
        """str: The root element of the content"""
        return 'potential-LAMMPS'
    
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
        
        pot = self.content[self.contentroot]
        params = {}
        params['key'] = pot['key']
        params['id'] = pot['id']
        params['pot_key'] = pot['potential']['key']
        params['pot_id'] = pot['potential']['id']
        params['units'] = pot['units']
        params['atom_style'] = pot['atom_style']
        params['pair_style'] = pot['pair_style']['type']
        
        params['elements'] = []
        params['masses'] = []
        params['symbols'] = []
        params['charge'] = []
        
        for atom in pot.iteraslist('atom'):
            params['elements'].append(atom.get('element', np.nan))
            params['masses'].append(atom.get('mass', np.nan))
            params['symbols'].append(atom.get('symbol', atom.get('element', np.nan)))
            params['charge'].append(atom.get('charge', np.nan))
        
        return params