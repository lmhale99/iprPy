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
    input_dict['strain_range'] = float(input_dict.get('strain_range', 1e-5))
    input_dict['pressure_xx'] = input.value_unit(input_dict, 'pressure_xx', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    input_dict['pressure_yy'] = input.value_unit(input_dict, 'pressure_yy', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')
    input_dict['pressure_zz'] = input.value_unit(input_dict, 'pressure_zz', default_unit=input_dict['pressure_unit'], default_term='0.0 GPa')   
    
    return input_dict