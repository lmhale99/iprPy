import os
import numpy as np

from DataModelDict import DataModelDict as DM
import atomman as am
import atomman.unitconvert as uc
from ..term_extractor import term_extractor

def system_load(input_dict, load='load', load_options='load_options', 
                box_parameters='box_parameters', symbols='symbols', 
                system_family='system_family', system_potential='system_potential', 
                ucell='ucell'):
    """
    Process input terms associated with a system to be loaded.
    
    Arguments:
    input_dict -- dictionary of input terms to process.
    
    Keyword Arguments:
    load -- key in input_dict where a load command is stored.
            Default value is 'load'.
    load_options -- key in input_dict for the load_options associated with load is stored.
                    Default value is 'load_options'.
    box_parameters -- key in input_dict for the box_parameters associated with load is stored.
                      Default value is 'box_parameters'.
    symbols -- key in input_dict where the list of symbols associated with load is stored.
               Default value is 'symbols'.
    system_family -- key in input_dict where load's system family will be saved.
                     Default value is 'system_family'.
    system_potential -- key in input_dict where load's system potential will be saved (if it has one).
                        Default value is 'system_potential'.                        
    ucell -- key in input_dict where the loaded unit cell system will be saved.
                     Default value is 'ucell'.
    """
    
    #Check for load command
    assert load in input_dict, load + ' value not supplied'
    
    #Set default values to optional keys
    input_dict[load_options] =   input_dict.get(load_options,   None)
    input_dict[box_parameters] = input_dict.get(box_parameters, None)
    input_dict[symbols] =        input_dict.get(symbols,        None)
    
    #split load command into style and file
    load_terms = input_dict[load].split(' ')
    assert len(load_terms) > 1, 'load value must specify both style and file'
    load_style = load_terms[0]
    load_file =  ' '.join(load_terms[1:])    
   
    #If load_style is system_model, check for system_family and system_potential
    if load_style == 'system_model':
        with open(load_file) as f:
            model = DM(f)
        
        #pass existing system_family name onto next generation
        try: input_dict[system_family] = model.find('system-info')['artifact']['family']
        #generate new system_family name using the load_file 
        except: input_dict[system_family] = os.path.splitext(os.path.basename(load_file))[0]
        
        #find if it is associated with a specific potential
        try: input_dict[system_potential] = model.find('potential')['key']
        except: pass
    
    #Other load_styles won't have a system family, so generate one using the load_file's name
    else: input_dict[system_family] = os.path.splitext(os.path.basename(load_file))[0]
    
    #Extract load_options terms
    kwargs= {}
    if input_dict[load_options] is not None:
        load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style', 'units', 'prop_info']
        kwargs = term_extractor(input_dict[load_options], {}, load_options_keys)
        if 'index' in kwargs: kwargs['index'] = int(kwargs['index']) 
        
    #Load ucell and symbols
    try:
        input_dict[ucell], load_symbols = am.load(load_style, load_file, **kwargs)
    except:
        input_dict[ucell] = None
        load_symbols = None

    #If symbols not given in calc input, save the symbols list from the loaded file
    if input_dict[symbols] is None: input_dict[symbols] = load_symbols
    
    #If symbols is given in calc input, use it
    else: input_dict[symbols] = input_dict[symbols].split(' ')    
       
    #Scale ucell by box_parameters
    if input_dict[ucell] is not None and input_dict[box_parameters] is not None:
        box_params = input_dict[box_parameters].split(' ')
        
        #len of 4 or 7 indicates that last term is a length unit
        if len(box_params) == 4 or len(box_params) == 7:
            unit = box_params[-1]
            box_params = box_params[:-1]
        
        #Use calculation's length_unit if unit not given in box_parameters
        else: unit = input_dict['length_unit']
        
        #Convert to the specified units
        box_params = uc.set_in_units(np.array(box_params, dtype=float), unit)
        
        #Three box_parameters means a, b, c
        if len(box_params) == 3:
            input_dict[ucell].box_set(a=box_params[0], b=box_params[1], c=box_params[2], scale=True) 
            
        #Six box_parameters means a, b, c, alpha, beta, gamma
        elif len(box_params) == 6:
            input_dict[ucell].box_set(a=box_params[0], b=box_params[1], c=box_params[2],
                                      alpha=box_params[0], beta=box_params[1], gamma=box_params[2], 
                                      scale=True) 
        else:
            ValueError('Invalid box_parameters command')