# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from ..boolean import boolean

__all__ = ['pointdefect']

def pointdefect(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with a point-defect record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'pointdefect_file'** a point-defect record to load.
    - **'pointdefect_content'** alternate file or content to load instead of
      specified pointdefect_file.  This is used by prepare functions.
    - **'pointdefect_model'** The open DataModelDict of the file/content
    - **'pointdefect_family'** the crystal family the defect parameters are specified for.
    - **'pointdefect_type'** defines the point defect type to add.
    - **'pointdefect_atype'** defines the atom type for the defect being
      added.
    - **'pointdefect_pos'** position to add the defect.
    - **'pointdefect_dumbbell_vect'** vector associated with a dumbbell
      interstitial.
    - **'pointdefect_scale'** indicates if pos and vect terms are scaled or
      unscaled.
    - **'ucell'** system unit cell. Used for scaling parameters.
    - **'calculation_params'** dictionary of point defect terms as read in.
    - **'point_kwargs'** dictionary of processed point defect terms as used by
      the atomman.defect.point function.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    build : bool
        If False, parameters will be interpreted, but objects won't be built
        from them (Default is True).
    pointdefect_file : str
        Replacement parameter key name for 'pointdefect_file'.
    pointdefect_content : str
        Replacement parameter key name for 'pointdefect_content'.
    pointdefect_model : str
        Replacement parameter key name for 'pointdefect_model'.
    pointdefect_family : str
        Replacement parameter key name for 'pointdefect_family'.
    pointdefect_type : str
        Replacement parameter key name for 'pointdefect_type'.
    pointdefect_atype : str
        Replacement parameter key name for 'pointdefect_atype'.
    pointdefect_pos : str
        Replacement parameter key name for 'pointdefect_pos'.
    pointdefect_dumbbell_vect : str
        Replacement parameter key name for 'pointdefect_dumbbell_vect'.
    pointdefect_scale : str
        Replacement parameter key name for 'pointdefect_scale'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    calculation_params : str
        Replacement parameter key name for 'calculation_params'.
    point_kwargs : str
        Replacement parameter key name for 'point_kwargs'.
    """
    
    # Set default keynames
    keynames = ['pointdefect_file', 'pointdefect_content', 'pointdefect_model',
                'pointdefect_family', 'pointdefect_type', 'pointdefect_atype',
                'pointdefect_pos', 'pointdefect_dumbbell_vect',
                'pointdefect_scale', 'ucell', 'calculation_params',
                'point_kwargs']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    pointdefect_file = input_dict.get(kwargs['pointdefect_file'], None)
    pointdefect_content = input_dict.get(kwargs['pointdefect_content'], None)
    
    # Replace defect model with defect content if given
    if pointdefect_content is not None:
        pointdefect_file = pointdefect_content
    
    # If defect model is given
    if pointdefect_file is not None:
        
        # Verify competing parameters are not defined
        for key in ('pointdefect_type', 'pointdefect_atype', 'pointdefect_pos',
                    'pointdefect_dumbbell_vect', 'pointdefect_scale'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '
                                                   + kwargs['pointdefect_file']
                                                   + ' cannot both be supplied')
        
        # Load defect model
        pointdefect_model = DM(pointdefect_file).find('point-defect')
        input_dict[kwargs['pointdefect_family']] = pointdefect_model['system-family']
        # Save raw parameters
        calculation_params = pointdefect_model['calculation-parameter']
    
    # Build calculation_params for given values
    else:
        calculation_params = DM()
        for key1, key2 in zip(('pointdefect_type', 'pointdefect_atype',
                               'pointdefect_pos', 'pointdefect_dumbbell_vect',
                               'pointdefect_scale'),
                              ('ptd_type', 'atype', 'pos', 'db_vect',
                               'scale')):
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
                processed['pos'] = np.array(raw['pos'].strip().split(),
                                            dtype=float)
                if scale is True:
                    processed['pos'] = ucell.unscale(processed['pos'])
            if 'db_vect' in raw:
            
                processed['db_vect'] = np.array(raw['db_vect'].strip().split(),
                                                dtype=float)
                if scale is True:
                    processed['db_vect'] = ucell.unscale(processed['db_vect'])
            
            processed['scale'] = False
            
            point_kwargs.append(processed)
        
        # Save processed terms
        input_dict[kwargs['point_kwargs']] = point_kwargs
    else:
        input_dict[kwargs['point_kwargs']] = None