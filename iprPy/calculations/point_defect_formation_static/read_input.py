from DataModelDict import DataModelDict as DM
from iprPy.tools import input
import atomman as am
import numpy as np

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = input.file_to_dict(f)
    
    #Interpret input terms common across calculations
    input.process_common_terms(input_dict, UUID)  
    
    if 'point_defect_model' in input_dict:
        assert 'point_defect_type'           not in input_dict, 'point_defect_type and point_defect_model cannot both be supplied'
        assert 'point_defect_atype'          not in input_dict, 'point_defect_atype and point_defect_model cannot both be supplied'
        assert 'point_defect_pos'            not in input_dict, 'point_defect_pos and point_defect_model cannot both be supplied'
        assert 'point_defect_aid'            not in input_dict, 'point_defect_aid and point_defect_model cannot both be supplied'
        assert 'point_defect_dumbbell_vect'  not in input_dict, 'point_defect_dumbbell_vect and point_defect_model cannot both be supplied'
        assert 'point_defect_scale'          not in input_dict, 'point_defect_scale and point_defect_model cannot both be supplied'
    
        with open(input_dict['point_defect_model']) as f:
            input_dict['point_defect_model'] = DM(f)
        
    else:
        input_dict['point_defect_model'] = DM()
        input_dict['point_defect_model']['point-defect-parameters'] = DM()
        input_dict['point_defect_model']['point-defect-parameters']['system-family'] = input_dict['system_family']
        input_dict['point_defect_model']['point-defect-parameters']['atomman-defect-point-parameters'] = ptd_params = DM()

        if 'point_defect_type' in input_dict:            
            if   input_dict['point_defect_type'].lower() in ['v', 'vacancy']:
                ptd_params['point_defect_type'] = 'v'
            elif input_dict['point_defect_type'].lower() in ['i', 'interstitial']:
                ptd_params['point_defect_type'] = 'i'
            elif input_dict['point_defect_type'].lower() in ['s', 'substitutional']:
                ptd_params['point_defect_type'] = 's'
            elif input_dict['point_defect_type'].lower() in ['d', 'db', 'dumbbell']:
                ptd_params['point_defect_type'] = 'db'  
            else:
                raise ValueError('invalid point_defect_type')
        if 'point_defect_atype' in input_dict:           
            ptd_params['atype'] = int(input_dict['point_defect_atype'])
        if 'point_defect_pos' in input_dict:             
            ptd_params['pos'] = list(np.array(input_dict['point_defect_pos'].split(), dtype=float))
        if 'point_defect_aid' in input_dict:             
            ptd_params['aid'] = int(input_dict['point_defect_aid'])
        if 'point_defect_dumbbell_vect' in input_dict:   
            ptd_params['db_vect'] =  list(np.array(input_dict['point_defect_dumbbell_vect'].split(), dtype=float))
        if 'point_defect_scale' in input_dict:           
            if input_dict['point_defect_scale'].lower() == 'true':
                ptd_params['scale'] = True
            elif input_dict['point_defect_scale'].lower() == 'false':
                ptd_params['scale'] = False
            else:
                raise ValueError('point_defect_scale must be True or False')
                
    #Read in input terms unique to this calculation
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    input_dict['force_tolerance'] = input.value_unit(input_dict, 'force_tolerance', default_unit=input_dict['force_unit'], default_term='1e-6 eV/angstrom')
    input_dict['maximum_iterations'] = int(input_dict.get('maximum_iterations', 100000))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 100000))
    
    return input_dict 