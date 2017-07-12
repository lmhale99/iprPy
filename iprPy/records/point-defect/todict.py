import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True, flat=False):

    model = DM(record)

    proto = model['point-defect']
    params = {}
    params['key'] =    proto['key']
    params['id'] =     proto['id']
    params['family'] = proto['system-family']
    
    params['ptd_type'] = []
    params['pos'] =      []
    params['atype'] =    []
    params['db_vect'] =  []
    params['scale'] =    []
    for cp in proto.iteraslist('calculation-parameter'):
        params['ptd_type'].append(cp.get('ptd_type', None))
        params['pos'].append(     cp.get('pos',      None))
        params['atype'].append(   cp.get('atype',    None))
        params['db_vect'].append( cp.get('db_vect',  None))
        params['scale'].append(   cp.get('scale',    None))

    return params 