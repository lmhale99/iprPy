from DataModelDict import DataModelDict as DM
from iprPy.tools import atomman_input
import atomman as am

def read_input(*args):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read in input terms. 
    #This also interprets terms consistent across the atomman-based calculations.
    input_dict = atomman_input.input(*args)
    
    #Interpret input terms unique to this calculation.
    input_dict['anneal_temperature'] = atomman_input.value_unit(input_dict.get('anneal_temperature', '0.0 K'), default_unit='K')
    input_dict['boundary_width'] = float(input_dict.get('boundary_width', 3.0))
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    input_dict['force_tolerance'] = atomman_input.value_unit(input_dict.get('force_tolerance', '1e-6 eV/angstrom'), default_unit=input_dict['force_unit'])
    input_dict['maximum_iterations'] = int(input_dict.get('maximum_iterations', 100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    input_dict['elastic_constants_model'] = input_dict.get('elastic_constants_model', input_dict['load'].split()[1])
    
    
    #Delete initial_system as it has not been rotated properly
    del(input_dict['initial_system'])
    
    #Extract elastic constants
    with open(input_dict['elastic_constants_model']) as f:
        input_dict['elastic_constants_model'] = DM(f)
        
    #Load the dislocation_model information
    with open(input_dict['dislocation_model']) as f:
        input_dict['dislocation_model'] = DM(f)       
    
    return input_dict