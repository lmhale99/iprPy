from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am

def read_input(f, uuid=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Load a dislocation model if given
    if 'dislocation_model' in input_dict:
        assert 'burgers'    not in input_dict, 'burgers and dislocation_model cannot both be supplied'
        assert 'atom_shift' not in input_dict, 'atom_shift and dislocation_model cannot both be supplied'
        assert 'x-axis'     not in input_dict, 'x-axis and dislocation_model cannot both be supplied'
        assert 'y-axis'     not in input_dict, 'y-axis and dislocation_model cannot both be supplied'
        assert 'z-axis'     not in input_dict, 'z-axis and dislocation_model cannot both be supplied'
        
        with open(input_dict['dislocation_model']) as f:
            input_dict['dislocation_model'] = DM(f) 
        
        params = input_dict['dislocation_model'].find('atomman-defect-Stroh-parameters')
        input_dict['burgers'] = params['burgers']
        input_dict['atom_shift'] = params['shift']
        input_dict['x-axis'] = params['crystallographic-axes']['x-axis']
        input_dict['y-axis'] = params['crystallographic-axes']['y-axis']
        input_dict['z-axis'] = params['crystallographic-axes']['z-axis']
        
    else:
        input_dict['dislocation_model'] = None
        assert 'burgers' in input_dict, 'burgers vector not given'
     
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, uuid)    
    
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
    
    #If no elastic constants defined
    if len(Cdict) == 0:
        #Check for elastic_constants_model
        if 'elastic_constants_model' in input_dict:
            with open(input_dict['elastic_constants_model']) as f:
                C_model = DM(f).find('elastic-constants')
            input_dict['elastic_constants_model'] = DM([('elastic-constants', C_model)])
            input_dict['C'] = am.tools.ElasticConstants(model=input_dict['elastic_constants_model'])
        #Check load file for elastic-constants
        else:    
            try:
                with open(input_dict['load'].split()[1]) as f:
                    C_model = DM(f).find('elastic-constants')
            except:
                raise ValueError('No elastic constants found!')
            input_dict['elastic_constants_model'] = DM([('elastic-constants', C_model)])
            input_dict['C'] = am.tools.ElasticConstants(model=input_dict['elastic_constants_model'])
        
    else:
        assert 'elastic_constants_model' not in input_dict, 'Cij values and elastic_constants_model cannot both be specified.'
        input_dict['elastic_constants_model'] = None 
        input_dict['C'] = am.tools.ElasticConstants(**Cdict)
        
    return input_dict