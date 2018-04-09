# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# http://www.numpy.org/
import numpy as np

def todict(record, full=True, flat=False):
    """
    Converts the XML content of a record to a dictionary.
    
    Parameters
    ----------
    record : iprPy.Record
        A record of the record style associated with this function.
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
    
    model = DM(record)

    pot = model['potential-LAMMPS']
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
        params['symbols'].append(atom.get('symbol', np.nan))
        params['charge'].append(atom.get('charge', np.nan))
    
    return params