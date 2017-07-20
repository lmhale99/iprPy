import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True, flat=False):

    model = DM(record)

    proto = model['free-surface']
    params = {}
    params['key'] =    proto['key']
    params['id'] =     proto['id']
    params['family'] = proto['system-family']
    
    calcparam = proto['calculation-parameter']
    params['x_axis'] =       calcparam['x_axis']
    params['y_axis'] =       calcparam['y_axis']
    params['z_axis'] =       calcparam['z_axis']
    params['atomshift'] =    calcparam['atomshift']
    params['cutboxvector'] = calcparam['cutboxvector']
    
    return params 