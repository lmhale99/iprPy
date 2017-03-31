import os

import numpy as np

from DataModelDict import DataModelDict as DM

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-dislocation-monopole.xsd')

def todict(record, full=True):

    model = DM(record)

    proto = model['dislocation-monopole']
    params = {}
    params['key'] =           proto['key']
    params['id'] =            proto['id']
    params['character'] =     proto['character']
    params['slipplane'] =     proto['slip-plane']
    params['linedirection'] = proto['line-direction']
    params['prototype'] =     proto['system-family']
    
    adsp = proto['atomman-defect-Stroh-parameters']
    params['x_axis'] =       np.array(adsp['crystallographic-axes']['x-axis'])
    params['y_axis'] =       np.array(adsp['crystallographic-axes']['y-axis'])
    params['z_axis'] =       np.array(adsp['crystallographic-axes']['z-axis'])
    params['burgers'] =      np.array(adsp['burgers'])
    params['atomshift'] =    np.array(adsp['atomshift'])
    
    return params 