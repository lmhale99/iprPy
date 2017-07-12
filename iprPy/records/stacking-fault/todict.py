import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True, flat=False):

    model = DM(record)

    proto = model['stacking-fault']
    params = {}
    params['key'] =    proto['key']
    params['id'] =     proto['id']
    params['family'] = proto['system-family']
    
    calcparam = proto['calculation-parameter']
    params['x_axis'] =        calcparam['x_axis']
    params['y_axis'] =        calcparam['y_axis']
    params['z_axis'] =        calcparam['z_axis']
    params['atomshift'] =     calcparam['atomshift']
    params['cutboxvector'] =  calcparam['cutboxvector']
    params['faultpos'] =      calcparam['faultpos']
    params['shiftvector1'] =  calcparam['shiftvector1']
    params['shiftvector2'] =  calcparam['shiftvector2']
    
    return params 