from DataModelDict import DataModelDict as DM
from iprPy.tools import atomman_input
import atomman as am

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
     
    #Interpret input terms common across calculations
    #Assert required keys exist
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    assert 'potential_file' in input_dict, 'potential_file value not supplied'
    assert 'load'           in input_dict, 'load value not supplied'
    
    #Set default values to optional keys
    if UUID is not None:
        input_dict['uuid'] =       UUID
    else:
        input_dict['uuid'] =       input_dict.get('uuid',           str(uuid.uuid4()))
    
    input_dict['mpi_command'] =    input_dict.get('mpi_command',    None)
    input_dict['potential_dir'] =  input_dict.get('potential_dir',  '')
    
    input_dict['length_unit'] =    input_dict.get('length_unit',    'angstrom')
    input_dict['energy_unit'] =    input_dict.get('energy_unit',    'eV')
    input_dict['pressure_unit'] =  input_dict.get('pressure_unit',  'GPa')
    input_dict['force_unit'] =     input_dict.get('force_unit',     'eV/angstrom') 
    
    input_dict['symbols'] =        input_dict.get('symbols',        None)
    
    #Read contents of potential_file into potential
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = DM(f)
    
    #Interpret input terms unique to this calculation.
    input_dict['boundary_shape'] =       input_dict.get('boundary_shape', 'circle')
    input_dict['boundary_width'] = float(input_dict.get('boundary_width', 3.0))
    
    input_dict['anneal_temperature'] = input.value_unit(input_dict, 'anneal_temperature', default_unit='K', default_term='0.0 K')    
    
    input_dict['energy_tolerance'] =  float(input_dict.get('energy_tolerance',    0.0))
    input_dict['force_tolerance'] =   input.value_unit(input_dict, 'force_tolerance', default_unit=input_dict['force_unit'], default_term='1e-6 eV/angstrom')
    input_dict['maximum_iterations'] =  int(input_dict.get('maximum_iterations',  100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    
    #input_dict['elastic_constants_model'] = input_dict.get('elastic_constants_model', input_dict['load'].split()[1])
    
    #Extract explicit elastic constants from input_dict
    Cdict = {}
    for key in input_dict.iterkeys():
        if key[0] == 'C':
            Cdict[key] = input.value_unit(input_dict, key, default_unit=input_dict['pressure_unit'])
    if len(Cdict) > 0:
        assert 'elastic_constants_model' not in input_dict, 'Cij values and elastic_constants_model cannot both be specified.'
        input_dict['elastic_constants_model'] = None 
        input_dict['C'] = am.tools.ElasticConstants(**Cdict)
    
    #If no Cij elastic constants defined check for elastic_constants_model
    else:
        #load file may be the elastic_constants_model file
        input_dict['elastic_constants_model'] = input_dict.get('elastic_constants_model', input_dict['load'].split()[1])
        
        with open(input_dict['elastic_constants_model']) as f:
            C_model = DM(f)
            
        try:
            input_dict['elastic_constants_model'] = DM([('elastic-constants', C_model.find('elastic-constants'))])
            input_dict['C'] = am.tools.ElasticConstants(model=input_dict['elastic_constants_model'])
        except:
            input_dict['elastic_constants_model'] = None 
            input_dict['C'] = None 
        
    return input_dict