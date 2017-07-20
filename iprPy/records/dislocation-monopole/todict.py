import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True):

    model = DM(record)

    proto = model['dislocation-monopole']
    params = {}
    params['key'] =           proto['key']
    params['id'] =            proto['id']
    params['character'] =     proto['character']
    params['burgersstring'] = proto['Burgers-vector']
    params['slipplane'] =     proto['slip-plane']
    params['linedirection'] = proto['line-direction']
    params['family'] =        proto['system-family']
    
    calcparam = proto['calculation-parameter']
    params['x_axis'] =        calcparam['x_axis']
    params['y_axis'] =        calcparam['y_axis']
    params['z_axis'] =        calcparam['z_axis']
    params['atomshift'] =     calcparam['atomshift']
    params['burgersvector'] = calcparam['burgersvector']
    
    return params 