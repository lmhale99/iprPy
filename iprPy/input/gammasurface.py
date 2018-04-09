# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman as am

def gammasurface(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with a 
    calculation_generalized_stacking_fault record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'gammasurface_model'** a calculation record to load.
    - **'gammasurface_content'** alternate file or content to load instead of
      specified dislocation_model.  This is used by prepare functions.
    - **'ucell'** the unit cell system. Used here in scaling the model
      parameters to the system being explored.
    - **'gamma'** the GammaSurface object created from the other keys.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    gammasurface_model : str
        Replacement parameter key name for 'gammasurface_model'.
    gammasurface_content : str
        Replacement parameter key name for 'gammasurface_content'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    gamma : str
        Replacement parameter key name for 'gamma'.
    """
    
    # Set default keynames
    keynames = ['gammasurface_model', 'gammasurface_content', 'ucell', 'gamma']
    
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
        
    # Extract input values and assign default values
    gammasurface_model = input_dict.get(kwargs['gammasurface_model'], None)
    gammasurface_content = input_dict.get(kwargs['gammasurface_content'], None)
    ucell = input_dict.get(kwargs['ucell'], None)
    
    # Replace defect model with defect content if given
    if gammasurface_content is not None:
        gammasurface_model = gammasurface_content
    
    # If defect model is given
    if gammasurface_model is not None:
        pass
    
    else:
        raise ValueError('gammasurface_model is required')
    
    # Get ucell's box
    if ucell is not None:
        box = ucell.box
    else:
        box = am.Box()
    
    if build is True:
        gamma = am.defect.GammaSurface(model=gammasurface_model, box=box)
    else:
        gamma = None
    
    input_dict['gamma'] = gamma