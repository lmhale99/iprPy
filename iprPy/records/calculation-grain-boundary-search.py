from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-grain-boundary-search.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-grain-boundary-search']
    params = {}
    params['calc_key'] =      calc['key']
    params['calc_script'] =   calc['calculation']['script']
    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    params['x_axis_1'] =      calc['grain-1']['crystallographic-axes']['x-axis']
    params['y_axis_1'] =      calc['grain-1']['crystallographic-axes']['y-axis']
    params['z_axis_1'] =      calc['grain-1']['crystallographic-axes']['z-axis']
    params['x_axis_2'] =      calc['grain-2']['crystallographic-axes']['x-axis']
    params['y_axis_2'] =      calc['grain-2']['crystallographic-axes']['y-axis']
    params['z_axis_2'] =      calc['grain-2']['crystallographic-axes']['z-axis']
    
    if full is True:
        if 'error' in calc:
            params['status'] = calc['status']
            params['error'] = calc['error']
            params['E_gb'] = np.nan
        
        elif 'status' in calc:
            params['status'] = calc['status']
            params['error'] = np.nan
            params['E_gb'] = np.nan
            
        else:
            params['status'] = np.nan
            params['error'] = np.nan
            params['E_gb'] = uc.value_unit(calc['lowest-energy']['E_gb'])
        
    return params 