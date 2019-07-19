from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am
import os

def read_input(f, uuid=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Check that shift, x-axis, y-axis, z-axis not given or have default values
    if 'shift' in input_dict and float(input_dict['shift']) != 0.0:
        raise ValueError('shift not allowed with bain_transformation')
    if 'x-axis' in input_dict and input_dict['x-axis'] != '1 0 0':
        raise ValueError('x-axis not allowed with bain_transformation')
    if 'y-axis' in input_dict and input_dict['x-axis'] != '0 1 0':
        raise ValueError('y-axis not allowed with bain_transformation')
    if 'z-axis' in input_dict and input_dict['x-axis'] != '0 0 1':
        raise ValueError('z-axis not allowed with bain_transformation')
    
    #Process 
    input.process_common_terms(input_dict)    
    
    #Interpret input terms unique to this calculation.
    input_dict['bain_a_scale'] = float(input_dict['bain_a_scale'])
    input_dict['bain_c_scale'] = float(input_dict['bain_c_scale'])
    input_dict['energy_tolerance'] =  float(input_dict.get('energy_tolerance',    0.0))
    input_dict['force_tolerance'] =   input.value_unit(input_dict, 'force_tolerance', default_unit=input_dict['force_unit'], default_term='1e-6 eV/angstrom')
    input_dict['maximum_iterations'] =  int(input_dict.get('maximum_iterations',  100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
     
    
    return input_dict