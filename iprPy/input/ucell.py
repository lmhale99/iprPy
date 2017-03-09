import numpy as np

import atomman as am
import atomman.unitconvert as uc
from ..tools import termtodict

def ucell(input_dict, **kwargs):
    """
    Builds an atomman.System based on input dict terms for loading an atomic 
    configuration. 
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    load -- load command containing a load style and load file path.
    load_options -- any additional options associated with loading the load 
                    file as an atomman.System.
    box_parameters -- the string of box parameters to scale the system by. 
                      Optional if the load file already is properly scaled.
    symbols -- the string list of symbols associated with the system's atomic
               types. Optional if the load file contains symbols information, 
               in which case symbols is assigned those values.
    ucell -- this is where the resulting system is saved.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    load -- replacement parameter key name for 'load'
    load_options -- replacement parameter key name for 'load_options'
    box_parameters -- replacement parameter key name for 'box_parameters'
    symbols -- replacement parameter key name for 'symbols'
    ucell -- replacement parameter key name for 'ucell'
    """   
       
    #Set default keynames
    keynames = ['load', 'load_options', 'box_parameters', 'symbols', 'ucell']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #Set default values
    input_dict[kwargs['load_options']] =   input_dict.get(kwargs['load_options'],   None)
    input_dict[kwargs['box_parameters']] = input_dict.get(kwargs['box_parameters'], None)
    input_dict[kwargs['symbols']] =        input_dict.get(kwargs['symbols'],        None)
    
    #split load command into style and file
    load_terms = input_dict[kwargs['load']].split(' ')
    assert len(load_terms) > 1, kwargs['load'] + ' value must specify both style and file'
    load_style = load_terms[0]
    load_file =  input_dict[kwargs['load']].replace(load_style, '', 1).strip()
    
    #Extract load_options terms
    load_options_kwargs= {}
    if input_dict[kwargs['load_options']] is not None:
        load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style', 'units', 'prop_info']
        load_options_kwargs = termtodict(input_dict[kwargs['load_options']], load_options_keys)
        if 'index' in load_options_kwargs: load_options_kwargs['index'] = int(load_options_kwargs['index']) 
        
    #Load ucell and symbols
    input_dict[kwargs['ucell']], load_symbols = am.load(load_style, load_file, **load_options_kwargs)

    #If symbols not given in input_dict, save the symbols list from the loaded file
    if input_dict[kwargs['symbols']] is None: input_dict[kwargs['symbols']] = load_symbols
    
    #If symbols is given in input_dict, use it
    else: input_dict[kwargs['symbols']] = input_dict[kwargs['symbols']].split(' ')    
       
    #Scale ucell by box_parameters
    if input_dict[kwargs['box_parameters']] is not None:
        box_params = input_dict[kwargs['box_parameters']].split(' ')
        
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
            input_dict[kwargs['ucell']].box_set(a=box_params[0], b=box_params[1], c=box_params[2], scale=True) 
            
        #Six box_parameters means a, b, c, alpha, beta, gamma
        elif len(box_params) == 6:
            input_dict[kwargs['ucell']].box_set(a=box_params[0], b=box_params[1], c=box_params[2],
                                      alpha=box_params[3], beta=box_params[4], gamma=box_params[5], 
                                      scale=True) 
        else: ValueError('Invalid box_parameters command')