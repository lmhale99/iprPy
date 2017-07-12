import numpy as np

from DataModelDict import DataModelDict as DM

from .boolean import boolean

def pointdefect(input_dict, build=True, **kwargs):
    """
    Reads in calculation parameters associated with a point-defect record.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    pointdefect_model -- a point-defect record to load.
    pointdefect_content -- alternate file or content to load instead of specified 
                       pointdefect_model. This is used by prepare functions.
    pointdefect_type -- defines the point defect type to add
    pointdefect_atype -- defines the atom type for the defect being added
    pointdefect_pos -- position to add the defect
    pointdefect_dumbbell_vect -- vector associated with a dumbbell interstitial
    pointdefect_scale -- indicates if pos and vect terms are scaled or unscaled
    ucell -- system unit cell. Used for scaling parameters
    calculation_params -- dictionary of point defect terms as read in
    point_kwargs -- dictionary of processed point defect terms as used by the 
                    atomman.defect.point function.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    build -- indicates if point_kwargs should be built
    pointdefect_model -- replacement parameter key name for 'pointdefect_model'
    pointdefect_content -- replacement parameter key name for 'pointdefect_content'
    pointdefect_type -- replacement parameter key name for 'pointdefect_type'
    pointdefect_atype -- replacement parameter key name for 'pointdefect_atype'
    pointdefect_pos -- replacement parameter key name for 'pointdefect_pos'
    pointdefect_dumbbell_vect -- replacement parameter key name for 'pointdefect_dumbbell_vect'
    pointdefect_scale -- replacement parameter key name for 'pointdefect_scale'
    ucell -- replacement parameter key name for 'ucell'
    calculation_params -- replacement parameter key name for 'calculation_params'
    point_kwargs -- replacement parameter key name for 'point_kwargs'
    
    """
    
    # Set default keynames
    keynames = ['pointdefect_model', 'pointdefect_content', 'pointdefect_type', 
                'pointdefect_atype', 'pointdefect_pos', 'pointdefect_dumbbell_vect',
                'pointdefect_scale', 'ucell', 'calculation_params', 'point_kwargs']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    pointdefect_model =   input_dict.get(kwargs['pointdefect_model'],   None)
    pointdefect_content = input_dict.get(kwargs['pointdefect_content'], None)
    
    # Replace defect model with defect content if given
    if pointdefect_content is not None:
        pointdefect_model = pointdefect_content
    
    # If defect model is given
    if pointdefect_model is not None:
        
        # Verify competing parameters are not defined
        for key in ('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos', 
                    'pointdefect_dumbbell_vect', 'pointdefect_scale'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '+ kwargs['pointdefect_model'] + 
                                                   ' cannot both be supplied')
        
        # Load defect model
        pointdefect_model = DM(pointdefect_model).find('point-defect')
            
        # Save raw parameters
        calculation_params = pointdefect_model['calculation-parameter']
    
    # Build calculation_params for given values
    else:
        calculation_params = DM()
        for key1, key2 in zip(('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos', 
                               'pointdefect_dumbbell_vect', 'pointdefect_scale'),
                              ('ptd_type', 'atype', 'pos', 'db_vect', 'scale')):
            if kwargs[key1] in input_dict:
                calculation_params[key2] = input_dict[kwargs[key1]]
    
    # Save processed terms
    input_dict[kwargs['pointdefect_model']] = pointdefect_model
    input_dict[kwargs['calculation_params']] = calculation_params
        
    # Build point_kwargs from calculation_params
    if build is True:
        ucell = input_dict[kwargs['ucell']]
        if not isinstance(calculation_params, (list, tuple)):
            calculation_params = [calculation_params]
        
        # Process parameters for running
        point_kwargs = []
        for raw in calculation_params:
            processed = {}
            
            scale = boolean(raw.get('scale', False))
            
            if 'ptd_type' in raw:
                if   raw['ptd_type'].lower() in ['v', 'vacancy']:
                    processed['ptd_type'] = 'v'
                elif raw['ptd_type'].lower() in ['i', 'interstitial']:
                    processed['ptd_type'] = 'i'
                elif raw['ptd_type'].lower() in ['s', 'substitutional']:
                    processed['ptd_type'] = 's'
                elif raw['ptd_type'].lower() in ['d', 'db', 'dumbbell']:
                    processed['ptd_type'] = 'db'  
                else:
                    raise ValueError('invalid ptd_type')

            if 'atype' in raw:
                processed['atype'] = int(raw['atype'])
                
            if 'pos' in raw:
                processed['pos'] = np.array(raw['pos'].strip().split(), dtype=float)
                if scale is True:
                    processed['pos'] = ucell.unscale(processed['pos'])
            if 'db_vect' in raw:
            
                processed['db_vect'] = np.array(raw['db_vect'].strip().split(), dtype=float)
                if scale is True:
                    processed['db_vect'] = ucell.unscale(processed['db_vect'])
            
            processed['scale'] = False
            
            point_kwargs.append(processed)
        
        # Save processed terms
        input_dict[kwargs['point_kwargs']] = point_kwargs
    else:
        input_dict[kwargs['point_kwargs']] = None