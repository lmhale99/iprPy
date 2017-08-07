from __future__ import division, absolute_import, print_function

import numpy as np

from DataModelDict import DataModelDict as DM

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

    proto = model['point-defect']
    params = {}
    params['key'] = proto['key']
    params['id'] = proto['id']
    params['family'] = proto['system-family']
    
    params['ptd_type'] = []
    params['pos'] = []
    params['atype'] = []
    params['db_vect'] = []
    params['scale'] = []
    for cp in proto.iteraslist('calculation-parameter'):
        params['ptd_type'].append(cp.get('ptd_type', None))
        params['pos'].append(cp.get('pos', None))
        params['atype'].append(cp.get('atype', None))
        params['db_vect'].append(cp.get('db_vect', None))
        params['scale'].append(cp.get('scale', None))

    return params