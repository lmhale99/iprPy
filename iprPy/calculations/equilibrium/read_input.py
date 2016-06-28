from DataModelDict import DataModelDict as DM
import iprPy
import atomman as am

def read_input(*args):
    """Handles the input commands for this calculation."""
    
    #Read in input terms consistent across the atomman-based calculations
    input_dict = iprPy.tools.atomman_input.input(*args)
    
    #Read in input terms unique to this calculation
    input_dict['thermo_steps'] = int(input_dict.get('thermo_steps', 1000))
    input_dict['pressure'] = iprPy.tools.atomman_input.value_unit(input_dict.get('pressure', '0.0'), default_unit=input_dict['pressure_unit'])
    input_dict['dump_every'] = int(input_dict.get('dump_every', 100000))
    input_dict['run_steps'] = int(input_dict.get('run_steps', 100000))
    input_dict['random_seed'] = int(input_dict.get('random_seed', 1734812))
    input_dict['temperature'] = float(input_dict.get('temperature', 0.0))
    
    
    #Convert ucell box mult terms to single integers
    try: input_dict['a_mult'] = input_dict['a_mult'][1] - input_dict['a_mult'][0]
    except: pass
    try: input_dict['b_mult'] = input_dict['b_mult'][1] - input_dict['b_mult'][0]
    except: pass
    try: input_dict['c_mult'] = input_dict['c_mult'][1] - input_dict['c_mult'][0]
    except: pass
    
    return input_dict