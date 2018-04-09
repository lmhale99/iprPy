# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

# iprPy imports
from ..tools import termtodict

def systemload(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with building a ucell system.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'load_file'** file to load system information from.
    - **'load_style'** file format of load_file. 
    - **'load_content'** alternate file or content to load instead of
      specified load_file.  This is used by prepare functions.
    - **'load_options'** any additional options associated with loading the
      load file as an atomman.System.
    - **'symbols'** the list of atomic symbols associated with ucell's atom
      types.  Optional if this information is in load/load_content.
    - **'box_parameters'** the string of box parameters to scale the system
      by.  Optional if the load file already is properly scaled.
    - **'system_family'** if the load file contains a system_family term, then
      it is passed on. Otherwise, a new system_family is created based on the
      load file's name.
    - **'ucell'** this is where the resulting system is saved.
    - **'symbols'** the list of atomic symbols associated with ucell's atom
      types. This is either taken from the load file or the load_symbols key.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    build : bool
        If False, parameters will be interpreted, but objects won't be built
        from them (Default is True).
    load_file : str
        Replacement parameter key name for 'load_file'.
    load_style : str
        Replacement parameter key name for 'load_style'.
    load_options : str
        Replacement parameter key name for 'load_options'.
    symbols : str
        Replacement parameter key name for 'symbols'.
    box_parameters : str
        Replacement parameter key name for 'box_parameters'.
    system_family : str
        Replacement parameter key name for 'system_family'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    """
       
    # Set default keynames
    keynames = ['load_file', 'load_style', 'load_options', 'load_content',
                'box_parameters', 'system_family', 'ucell', 'symbols']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    load_file = input_dict[kwargs['load_file']]
    load_style = input_dict.get(kwargs['load_style'], 'system_model')
    load_options = input_dict.get(kwargs['load_options'], None)
    load_content = input_dict.get(kwargs['load_content'], None)
    symbolsgiven = input_dict.get(kwargs['symbols'], None)
    box_parameters = input_dict.get(kwargs['box_parameters'], None)
    
    # Use load_content instead of load_file if given
    if load_content is not None:
        load_file = load_content
    
    # Separate load_options terms
    load_options_kwargs= {}
    if load_options is not None:
        load_options_keys = ['key', 'index', 'data_set', 'pbc', 'atom_style',
                             'units', 'prop_info']
        load_options_kwargs = termtodict(load_options, load_options_keys)
        if 'index' in load_options_kwargs:
            load_options_kwargs['index'] = int(load_options_kwargs['index'])
    
    # Build ucell
    if build is True:
        # Load ucell and symbols
        ucell = am.load(load_style, load_file, **load_options_kwargs)
        
        # Scale ucell by box_parameters
        if box_parameters is not None:
            box_params = box_parameters.split()
            
            # len of 4 or 7 indicates that last term is a length unit
            if len(box_params) == 4 or len(box_params) == 7:
                unit = box_params[-1]
                box_params = box_params[:-1]
            
            # Use calculation's length_unit if unit not given in box_parameters
            else: 
                unit = input_dict['length_unit']
            
            # Convert to the specified units
            box_params = np.array(box_params, dtype=float)
            box_params[:3] = uc.set_in_units(box_params[:3], unit)
            
            # Three box_parameters means a, b, c
            if len(box_params) == 3:
                ucell.box_set(a=box_params[0], b=box_params[1],
                              c=box_params[2], scale=True)
                
            # Six box_parameters means a, b, c, alpha, beta, gamma
            elif len(box_params) == 6:
                ucell.box_set(a=box_params[0], b=box_params[1], c=box_params[2],
                              alpha=box_params[3], beta=box_params[4],
                              gamma=box_params[5], scale=True) 
            
            # Other options are invalid
            else: 
                ValueError('Invalid box_parameters command')
    
    # Don't build ucell 
    else:
        ucell = None
    
    # Replace symbols with symbolsgiven
    if symbolsgiven is not None:
        ucell.symbols = symbolsgiven.split()
        
    # Extract system_family (and possibly symbols) from system_model
    if load_style == 'system_model':
        model = DM(load_file)
        
        # If model is a crystal-prototype, the system_family is it's id
        if model.keys()[0] == 'crystal-prototype':
            system_family = model['crystal-prototype']['id']
        
        # Extract system_family from the model
        else:
            try:
                system_family = model.find('system-info')['family']
            except:
                system_family = None
        
        # Extract symbols if needed
        if symbols[0] is None:
            symbols = model.find('system-info')['symbol']
    
    # If not system_model, system_family is load_file's basename
    else:
        system_family = os.path.splitext(os.path.basename(load_file))[0]
            
    # Save processed terms
    input_dict[kwargs['load_style']] = load_style
    input_dict[kwargs['load_options']] = load_options
    input_dict[kwargs['box_parameters']] = box_parameters
    input_dict[kwargs['system_family']] = system_family
    input_dict[kwargs['ucell']] = ucell
    input_dict[kwargs['symbols']] = symbols