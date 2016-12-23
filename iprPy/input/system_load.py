import os
import numpy as np

from DataModelDict import DataModelDict as DM
import atomman as am
import atomman.unitconvert as uc
from ..tools import termtodict

def system_load(input_dict, **kwargs):
    """
    Handles input parameters associated with the initial loading of an atomic 
    system.
    1. Checks that 'load' is given in input file
    2. Sets default value of None to 'load_options' term if needed.
    3. Sets default value of None to 'box_parameters' term if needed.
    4. Sets default value of None to 'symbols' term if needed.
    5. Identifies 'system_family' value from the 'load' file if needed.
    6. Sets 'system_potential' value if listed in 'load' file.
    7. Constructs unit cell system 'ucell' by opening 'load' file and applying 
       'box_parameters' if needed.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    load -- replacement parameter key name for 'load'
    load_options -- replacement parameter key name for 'load_options'
    box_parameters -- replacement parameter key name for 'box_parameters'
    symbols -- replacement parameter key name for 'symbols'
    system_family -- replacement parameter key name for 'system_family'
    system_potential -- replacement parameter key name for 'system_potential'
    ucell -- replacement parameter key name for 'ucell'
    """   
       
    #Set default keynames
    keynames = ['load', 'load_options', 'box_parameters', 'symbols', 
                'system_family', 'system_potential', 'ucell']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)

    #Check for load command
    assert kwargs['load'] in input_dict, kwargs['load'] + ' value not supplied'
    
    #Set default values to optional keys
    input_dict[kwargs['load_options']] =   input_dict.get(kwargs['load_options'],   None)
    input_dict[kwargs['box_parameters']] = input_dict.get(kwargs['box_parameters'], None)
    input_dict[kwargs['symbols']] =        input_dict.get(kwargs['symbols'],        None)
    
    #split load command into style and file
    load_terms = input_dict[kwargs['load']].split(' ')
    assert len(load_terms) > 1, kwargs['load'] + ' value must specify both style and file'
    load_style = load_terms[0]
    load_file =  ' '.join(load_terms[1:])    
   
    #If load_style is system_model, check for system_family and system_potential
    if load_style == 'system_model':
        with open(load_file) as f:
            model = DM(f)
        
        #pass existing system_family name onto next generation
        try: input_dict[kwargs['system_family']] = model.find('system-info')['artifact']['family']
        #generate new system_family name using the load_file 
        except: input_dict[kwargs['system_family']] = os.path.splitext(os.path.basename(load_file))[0]
        
        #find if it is associated with a specific potential
        try: input_dict[kwargs['system_potential']] = model.find('potential')['key']
        except: pass
    
    #Other load_styles won't have a system family, so generate one using the load_file's name
    else: input_dict[kwargs['system_family']] = os.path.splitext(os.path.basename(load_file))[0]
    
    #Extract load_options terms
    kwargs= {}
    if input_dict[kwargs['load_options']] is not None:
        load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style', 'units', 'prop_info']
        kwargs = termtodict(input_dict[kwargs['load_options']], load_options_keys)
        if 'index' in kwargs: kwargs['index'] = int(kwargs['index']) 
        
    #Load ucell and symbols
    try:
        input_dict[kwargs['ucell']], load_symbols = am.load(load_style, load_file, **kwargs)
    except:
        input_dict[kwargs['ucell']] = None
        load_symbols = None

    #If symbols not given in calc input, save the symbols list from the loaded file
    if input_dict[kwargs['symbols']] is None: input_dict[kwargs['symbols']] = load_symbols
    
    #If symbols is given in calc input, use it
    else: input_dict[kwargs['symbols']] = input_dict[kwargs['symbols']].split(' ')    
       
    #Scale ucell by box_parameters
    if input_dict[kwargs['ucell']] is not None and input_dict[kwargs['box_parameters']] is not None:
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
                                      alpha=box_params[0], beta=box_params[1], gamma=box_params[2], 
                                      scale=True) 
        else:
            ValueError('Invalid box_parameters command')