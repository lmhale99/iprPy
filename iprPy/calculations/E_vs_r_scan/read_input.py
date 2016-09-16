from iprPy.tools import input

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, UUID)  
    
    #Interpret input terms unique to this calculation.
    input_dict['minimum_r'] = input.value_unit(input_dict, 'minimum_r', default_unit=input_dict['length_unit'], default_term='2.0 angstrom')
    input_dict['maximum_r'] = input.value_unit(input_dict, 'maximum_r', default_unit=input_dict['length_unit'], default_term='6.0 angstrom')
    input_dict['number_of_steps_r'] = int(input_dict.get('number_of_steps_r', 200))
    
    return input_dict