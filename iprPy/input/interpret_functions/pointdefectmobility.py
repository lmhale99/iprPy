# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

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
    keynames = ['pointdefect_mobility_file', 'pointdefect_mobility_model',
                'pointdefect_mobility_family', 'ucell', 'initial_calculation_params',
                'start_calculation_params','end_calculation_params',
                'initialdefect_number','defectpair_number','point_mobility_kwargs']
                
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    pointdefect_mobility_file = input_dict.get(kwargs['pointdefect_mobility_file'], None)
    
    
    # If defect model is given
    if pointdefect_mobility_file is not None:
        
            
        # Load defect model
        
        pointdefect_mobility_model = DM(pointdefect_mobility_file).find('point-defect-mobility')
        input_dict[kwargs['pointdefect_mobility_family']] = pointdefect_mobility_model['system-family']
        
        #Interpreting premade files here
        input_dict['initialdefect_number'] = pointdefect_mobility_model['initial-defect-number']
        input_dict['defect_pair_number'] = pointdefect_mobility_model['defect-pair-number']
        initial_calculation_params = pointdefect_mobility_model['initial-calculation-parameters']
        start_calculation_params = pointdefect_mobility_model['start-calculation-parameters']
        end_calculation_params = pointdefect_mobility_model['end-calculation-parameters']
        input_dict['allSymbols'] = input_dict.get('allSymbols', input_dict['symbols']).split(' ')
        input_dict[kwargs['pointdefect_mobility_model']] = pointdefect_mobility_model

    # Build calculation_params for given values
    else:
        input_dict['initialdefect_number'] = input_dict.get(kwargs['initialdefect_number'], 0)
        input_dict['defect_pair_number'] = input_dict.get(kwargs['defectpair_number'], None)
        input_dict['allSymbols'] = input_dict.get('allSymbols', input_dict['symbols']).split(' ')
        initial_calculation_params = []
        if int(input_dict['initialdefect_number'])>0:
            for x in range(int(input_dict['initialdefect_number'])):
                defect_type_string = str('initial_pointdefect_type_'+str(x))
                defect_atype_string = str('initial_pointdefect_atype_'+str(x))
                defect_pos_string = str('initial_pointdefect_pos_'+str(x))
                defect_dumbell_string = str('initial_pointdefect_dumbbell_vect_'+str(x))
                defect_scale_string = str('initial_pointdefect_scale_'+str(x))
                addKeynames = [defect_type_string , defect_atype_string , defect_pos_string , defect_dumbell_string , defect_scale_string]
                for addKeynames in addKeynames:
                    kwargs[addKeynames] = kwargs.get(addKeynames, addKeynames)
                newParams= {}
                for key1, key2 in zip((defect_type_string, defect_atype_string,
                               defect_pos_string, defect_dumbell_string,
                               defect_scale_string),('ptd_type', 'atype', 'pos', 'db_vect',
                               'scale')):
                    if kwargs[key1] in input_dict:
                        newParams[key2] = input_dict[kwargs[key1]]
                initial_calculation_params.append(newParams)
                
        if int(input_dict['defect_pair_number']) > 0:
            start_calculation_params =[]
            end_calculation_params=[]
            for x in range(int(input_dict['defect_pair_number'])):
                defect_type_string = str('start_pointdefect_type_'+str(x))
                defect_atype_string = str('start_pointdefect_atype_'+str(x))
                defect_pos_string = str('start_pointdefect_pos_'+str(x))
                defect_dumbell_string = str('start_pointdefect_dumbbell_vect_'+str(x))
                defect_scale_string = str('start_pointdefect_scale_'+str(x))
                addKeynames = [defect_type_string , defect_atype_string , defect_pos_string , defect_dumbell_string , defect_scale_string]
                for addKeynames in addKeynames:
                    kwargs[addKeynames] = kwargs.get(addKeynames, addKeynames)
                newParams= {}
                for key1, key2 in zip((defect_type_string, defect_atype_string,
                               defect_pos_string, defect_dumbell_string,
                               defect_scale_string),('ptd_type', 'atype', 'pos', 'db_vect',
                               'scale')):
                    if kwargs[key1] in input_dict:
                        newParams[key2] = input_dict[kwargs[key1]]
                start_calculation_params.append(newParams)
            for x in range(int(input_dict['defect_pair_number'])):
                defect_type_string = str('end_pointdefect_type_'+str(x))
                defect_atype_string = str('end_pointdefect_atype_'+str(x))
                defect_pos_string = str('end_pointdefect_pos_'+str(x))
                defect_dumbell_string = str('end_pointdefect_dumbbell_vect_'+str(x))
                defect_scale_string = str('end_pointdefect_scale_'+str(x))
                addKeynames = [defect_type_string , defect_atype_string , defect_pos_string , defect_dumbell_string , defect_scale_string]
                for addKeynames in addKeynames:
                    kwargs[addKeynames] = kwargs.get(addKeynames, addKeynames)
                newParams= {}
                for key1, key2 in zip((defect_type_string, defect_atype_string,
                               defect_pos_string, defect_dumbell_string,
                               defect_scale_string),('ptd_type', 'atype', 'pos', 'db_vect',
                               'scale')):
                    if kwargs[key1] in input_dict:
                        newParams[key2] = input_dict[kwargs[key1]]
                end_calculation_params.append(newParams)



    # Save processed terms

    
    input_dict[kwargs['initial_calculation_params']] = initial_calculation_params
    input_dict[kwargs['start_calculation_params']] = start_calculation_params
    input_dict[kwargs['end_calculation_params']] = end_calculation_params
    

    # Build point_kwargs from calculation_params
    if build is True:
        ucell = input_dict[kwargs['ucell']]
        if not isinstance(initial_calculation_params, (list, tuple)):
            initial_calculation_params = [initial_calculation_params]
            
        if not isinstance(start_calculation_params, (list, tuple)):
            start_calculation_params = [start_calculation_params]
        
        if not isinstance(end_calculation_params, (list, tuple)):
            end_calculation_params = [end_calculation_params]
        
        # Process parameters for running
        point_mobility_kwargs = DM()
        point_mobility_kwargs['initial'] = []
        point_mobility_kwargs['start'] = []
        point_mobility_kwargs['end'] = []

        for raw in initial_calculation_params:
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
            
            point_mobility_kwargs['initial'].append(processed)
        
        for raw in start_calculation_params:
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
            
            point_mobility_kwargs['start'].append(processed)
            
        for raw in end_calculation_params:
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
            
            point_mobility_kwargs['end'].append(processed)
        
        # Save processed terms

        input_dict[kwargs['point_mobility_kwargs']] = point_mobility_kwargs
    else:
        input_dict[kwargs['point_mobility_kwargs']] = None