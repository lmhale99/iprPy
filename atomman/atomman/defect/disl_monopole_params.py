import numpy as np
import atomman as am

def disl_monopole_params(datamodel):
    
    if isinstance(datamodel, (str, unicode)):
        datamodel = am.models.DataModel(datamodel)        

    monopole = datamodel.find('dislocation_monopole')
    assert len(monopole) == 1, 'Exactly one dislocation_monopole must be in the data model'
    monopole = monopole[0]

    ddict = {}
    ddict['burgers'] = np.array(monopole['simulation_parameters']['burgers_vector'], dtype=float)
    
    x_axis = np.array(monopole['simulation_parameters']['crystallographic_axes']['x-axis'], dtype=int)
    y_axis = np.array(monopole['simulation_parameters']['crystallographic_axes']['y-axis'], dtype=int)
    z_axis = np.array(monopole['simulation_parameters']['crystallographic_axes']['z-axis'], dtype=int)
    ddict['axes'] = np.array((x_axis, y_axis, z_axis))
    
    ddict['shift'] =    np.array(monopole['simulation_parameters']['shift'])
    ddict['z_width'] =  np.array(monopole['simulation_parameters']['width'])
    
    ddict['Nye_cutoff'] = float(monopole['Nye_tensor_parameters']['radial_cutoff']['value'])
    ddict['Nye_angle'] =  float(monopole['Nye_tensor_parameters']['bond_angle_cutoff']['value'])
    
    p = np.empty((len(monopole['Nye_tensor_parameters']['p_vector']), 3))
    for i in xrange(len(monopole['Nye_tensor_parameters']['p_vector'])):
        p[i] = np.array(monopole['Nye_tensor_parameters']['p_vector'][i]['value'])
    ddict['Nye_p'] = p
    
    return ddict
    
    