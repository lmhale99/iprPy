from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, UUID)  
    
    #Interpret input terms unique to this calculation.
    input_dict['thermo_steps'] = int(input_dict.get('thermo_steps', 1000))
    input_dict['pressure'] = input.value_unit(input_dict, 'pressure', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    input_dict['dump_every'] = int(input_dict.get('dump_every', 100000))
    input_dict['run_steps'] = int(input_dict.get('run_steps', 100000))
    input_dict['random_seed'] = int(input_dict.get('random_seed', 1734812))
    input_dict['integration'] = str(input_dict.get('integration', 'npt'))
    input_dict['temperature'] = float(input_dict.get('temperature', 0.001))
    
    return input_dict
