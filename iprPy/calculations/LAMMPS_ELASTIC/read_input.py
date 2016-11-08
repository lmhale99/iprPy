from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am
import uuid

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary
    input_dict = input.file_to_dict(f)
    
    #set calculation UUID
    if UUID is not None: input_dict['uuid'] = UUID
    else: input_dict['uuid'] = input_dict.get('uuid', str(uuid.uuid4()))
    
    #Process command lines
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    input_dict['mpi_command'] = input_dict.get('mpi_command', None)
    
    #Process potential
    input.lammps_potential(input_dict)
    
    #Process default units
    input.units(input_dict)
    
    #Process system information
    input.system_load(input_dict)
    
    #Process system manipulations
    if input_dict['ucell'] is not None:
        input.system_manipulate(input_dict)
    
    #Process run parameters
    #these are integer terms
    input_dict['maximum_iterations'] =  int(input_dict.get('maximum_iterations',  100))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 1000))
    
    #these are unitless floating point terms
    input_dict['strain_range'] =     float(input_dict.get('strain_range',     1e-6))
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    
    #these are terms with units
    input_dict['force_tolerance'] =       input.value_unit(input_dict, 'force_tolerance',       default_unit=input_dict['force_unit'],  default_term='1.0e-10 eV/angstrom')             
    input_dict['maximum_atomic_motion'] = input.value_unit(input_dict, 'maximum_atomic_motion', default_unit=input_dict['length_unit'], default_term='0.01 angstrom')
    
    return input_dict
    

        
    

    
        
        







    