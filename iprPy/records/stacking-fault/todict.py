import numpy as np

from DataModelDict import DataModelDict as DM

def todict(record, full=True, flat=False):

    model = DM(record)

    proto = model['stacking-fault']
    params = {}
    params['key'] =       proto['key']
    params['id'] =        proto['id']
    params['prototype'] = proto['system-family']
    
    asp = proto['atomman-stacking-fault-parameters']
    params['x_axis'] =         np.array(asp['crystallographic-axes']['x-axis'])
    params['y_axis'] =         np.array(asp['crystallographic-axes']['y-axis'])
    params['z_axis'] =         np.array(asp['crystallographic-axes']['z-axis'])
    params['atomshift'] =      np.array(asp['atomshift'])
    params['plane_axis'] =     asp['plane-axis']
    params['plane_position'] = float(asp['plane-position'])
    params['shift_vector_1'] = np.array(asp['shift-vector-1'])
    params['shift_vector_2'] = np.array(asp['shift-vector-2'])
    
    return params 