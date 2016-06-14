from DataModelDict import DataModelDict as DM
from iprPy.tools import atomman_input
import atomman as am

def read_input(*args):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read in input terms. 
    #This also interprets terms consistent across the atomman-based calculations.
    input_dict = atomman_input.input(*args)

    #Read in input terms unique to this calculation
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    input_dict['force_tolerance'] = atomman_input.value_unit(input_dict.get('force_tolerance', '1e-6 eV/angstrom'), default_unit=input_dict['force_unit'])
    input_dict['maximum_iterations'] = int(input_dict.get('maximum_iterations', 100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    
    with open(input_dict['ptd_model']) as f:
        input_dict['ptd_model'] = DM(f)
    
    #Convert ucell box mult terms to single integers
    try: input_dict['a_mult'] = input_dict['a_mult'][1] - input_dict['a_mult'][0]
    except: pass
    try: input_dict['b_mult'] = input_dict['b_mult'][1] - input_dict['b_mult'][0]
    except: pass
    try: input_dict['c_mult'] = input_dict['c_mult'][1] - input_dict['c_mult'][0]
    except: pass
    
    return input_dict