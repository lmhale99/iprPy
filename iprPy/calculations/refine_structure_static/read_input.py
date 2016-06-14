from DataModelDict import DataModelDict as DM
from iprPy.tools import atomman_input
import atomman as am

def read_input(*args):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read in input terms. 
    #This also interprets terms consistent across the atomman-based calculations.
    input_dict = atomman_input.input(*args)
    
    #Interpret input terms unique to this calculation.
    input_dict['strain_range'] = float(input_dict.get('strain_range', 1e-5))
    input_dict['pressure_xx'] = atomman_input.value_unit(input_dict.get('pressure_xx', '0.0'), default_unit=input_dict['pressure_unit'])
    input_dict['pressure_yy'] = atomman_input.value_unit(input_dict.get('pressure_yy', '0.0'), default_unit=input_dict['pressure_unit'])
    input_dict['pressure_zz'] = atomman_input.value_unit(input_dict.get('pressure_zz', '0.0'), default_unit=input_dict['pressure_unit'])
    
    #Convert ucell box mult terms to single integers
    try: input_dict['a_mult'] = input_dict['a_mult'][1] - input_dict['a_mult'][0]
    except: pass
    try: input_dict['b_mult'] = input_dict['b_mult'][1] - input_dict['b_mult'][0]
    except: pass
    try: input_dict['c_mult'] = input_dict['c_mult'][1] - input_dict['c_mult'][0]
    except: pass     
    
    return input_dict