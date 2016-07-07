from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am
import numpy as np

def read_input(f, uuid=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, uuid)  
    
    if 'ptd_model' in input_dict:
        assert 'ptd_type'           not in input_dict, 'ptd_type and ptd_model cannot both be supplied'
        assert 'ptd_atype'          not in input_dict, 'ptd_atype and ptd_model cannot both be supplied'
        assert 'ptd_pos'            not in input_dict, 'ptd_pos and ptd_model cannot both be supplied'
        assert 'ptd_aid'            not in input_dict, 'ptd_aid and ptd_model cannot both be supplied'
        assert 'ptd_dumbbell_vect'  not in input_dict, 'ptd_dumbbell_vect and ptd_model cannot both be supplied'
        assert 'ptd_scale'          not in input_dict, 'ptd_scale and ptd_model cannot both be supplied'
    
        with open(input_dict['ptd_model']) as f:
            input_dict['ptd_model'] = DM(f)
        
    else:
        input_dict['ptd_model'] = DM()
        input_dict['ptd_model']['point-defect-parameters'] = DM()
        input_dict['ptd_model']['point-defect-parameters']['system-family'] = input_dict['system_family']
        input_dict['ptd_model']['point-defect-parameters']['atomman-defect-point-parameters'] = ptd_params = DM()

        if 'ptd_type' in input_dict:            
            if   input_dict['ptd_type'].lower() in ['v', 'vacancy']:
                ptd_params['ptd_type'] = 'v'
            elif input_dict['ptd_type'].lower() in ['i', 'interstitial']:
                ptd_params['ptd_type'] = 'i'
            elif input_dict['ptd_type'].lower() in ['s', 'substitutional']:
                ptd_params['ptd_type'] = 's'
            elif input_dict['ptd_type'].lower() in ['d', 'db', 'dumbbell']:
                ptd_params['ptd_type'] = 'db'  
            else:
                raise ValueError('invalid ptd_type')
        if 'ptd_atype' in input_dict:           
            ptd_params['atype'] = int(input_dict['ptd_atype'])
        if 'ptd_pos' in input_dict:             
            ptd_params['pos'] = list(np.array(input_dict['ptd_pos'].split(), dtype=float))
        if 'ptd_aid' in input_dict:             
            ptd_params['aid'] = int(input_dict['ptd_aid'])
        if 'ptd_dumbbell_vect' in input_dict:   
            ptd_params['db_vect'] =  list(np.array(input_dict['ptd_dumbbell_vect'].split(), dtype=float))
        if 'ptd_scale' in input_dict:           
            if input_dict['ptd_scale'].lower() == 'true':
                ptd_params['scale'] = True
            elif input_dict['ptd_scale'].lower() == 'false':
                ptd_params['scale'] = False
            else:
                raise ValueError('ptd_scale must be True or False')
                
    #Read in input terms unique to this calculation
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    input_dict['force_tolerance'] = input.value_unit(input_dict, 'force_tolerance', default_unit=input_dict['force_unit'], default_term='1e-6 eV/angstrom')
    input_dict['maximum_iterations'] = int(input_dict.get('maximum_iterations', 100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    
    return input_dict 