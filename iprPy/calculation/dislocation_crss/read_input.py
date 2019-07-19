from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am

def read_input(f, uuid=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
        
    #Load a dislocation model if given
    if 'dislocation_model' in input_dict:
        assert 'x-axis'     not in input_dict, 'x-axis and dislocation_model cannot both be supplied'
        assert 'y-axis'     not in input_dict, 'y-axis and dislocation_model cannot both be supplied'
        assert 'z-axis'     not in input_dict, 'z-axis and dislocation_model cannot both be supplied'
        
        with open(input_dict['dislocation_model']) as f:
            input_dict['dislocation_model'] = DM(f) 
        
        params = input_dict['dislocation_model'].find('atomman-defect-Stroh-parameters')
        x_axis = params['crystallographic-axes']['x-axis']
        y_axis = params['crystallographic-axes']['y-axis']
        z_axis = params['crystallographic-axes']['z-axis']
        
    else:
        #Remove any axes so system is not rotated
        input_dict['dislocation_model'] = None
        x_axis = input_dict.pop('x-axis', [1,0,0])
        y_axis = input_dict.pop('y-axis', [0,1,0])
        z_axis = input_dict.pop('z-axis', [0,0,1])
        
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, uuid)    
    
    #Add axes back to input_dict
    input_dict['x-axis'] = x_axis
    input_dict['y-axis'] = y_axis
    input_dict['z-axis'] = z_axis    
    
    #Interpret input terms unique to this calculation.
    input_dict['chi_angle'] = float(input_dict.get('chi_angle', 0.0))
    input_dict['rss_steps'] = int(input_dict.get('rss_steps', 0))
    input_dict['sigma'] =     input.value_unit(input_dict, 'sigma', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa') 
    input_dict['tau_1'] =     input.value_unit(input_dict, 'tau_1', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    input_dict['tau_2'] =     input.value_unit(input_dict, 'tau_2', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    input_dict['press'] =     input.value_unit(input_dict, 'press', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    
    input_dict['energy_tolerance'] =  float(input_dict.get('energy_tolerance',    0.0))
    input_dict['force_tolerance'] =   input.value_unit(input_dict, 'force_tolerance', default_unit=input_dict['force_unit'], default_term='1e-6 eV/angstrom')
    input_dict['maximum_iterations'] =  int(input_dict.get('maximum_iterations',  100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    
    #Extract explicit elastic constants from input_dict
    Cdict = {}
    for key in input_dict.iterkeys():
        if key[0] == 'C':
            Cdict[key] = input.value_unit(input_dict, key, default_unit=input_dict['pressure_unit'])
    if len(Cdict) > 0:
        assert 'elastic_constants_model' not in input_dict, 'Cij values and elastic_constants_model cannot both be specified.'
        input_dict['elastic_constants_model'] = None 
        input_dict['C'] = am.ElasticConstants(**Cdict)
    
    #If no Cij elastic constants defined check for elastic_constants_model
    else:
        #load file may be the elastic_constants_model file
        input_dict['elastic_constants_model'] = input_dict.get('elastic_constants_model', input_dict['load'].split()[1])
        
        with open(input_dict['elastic_constants_model']) as f:
            C_model = DM(f)
            
        try:
            input_dict['elastic_constants_model'] = DM([('elastic-constants', C_model.find('elastic-constants'))])
            input_dict['C'] = am.ElasticConstants(model=input_dict['elastic_constants_model'])
        except:
            input_dict['elastic_constants_model'] = None 
            input_dict['C'] = None 
        
    return input_dict