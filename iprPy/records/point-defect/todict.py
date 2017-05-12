import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True, flat=False):

    model = DM(record)

    proto = model['point-defect']
    params = {}
    params['key'] =           proto['key']
    params['id'] =            proto['id']
    params['prototype'] =     proto['system-family']
    
    params['ptd_type'] = []
    params['pos'] =      []
    params['atype'] =    []
    params['db_vect'] =  []
    params['scale'] =    []
    for adpp in proto.iteraslist('atomman-defect-point-parameters'):
        params['ptd_type'].append(adpp.get('ptd_type', None))
        params['pos'].append(adpp.get('pos', None))
        params['atype'].append(adpp.get('atype', None))
        params['db_vect'].append(adpp.get('db_vect', None))
        params['scale'].append(adpp.get('scale', None))
    return params 