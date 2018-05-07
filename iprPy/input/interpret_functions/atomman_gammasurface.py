# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman as am

__all__ = ['atomman_gammasurface']

def atomman_gammasurface(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with a 
    calculation_generalized_stacking_fault record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'gammasurface_file'** a calculation record to load.
    - **'gammasurface_content'** alternate file or content to load instead of
      specified dislocation_model.  This is used by prepare functions.
    - **'ucell'** the unit cell system. Used here in scaling the model
      parameters to the system being explored.
    - **'gamma'** the GammaSurface object created from the other keys.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    gammasurface_file : str
        Replacement parameter key name for 'gammasurface_file'.
    gammasurface_content : str
        Replacement parameter key name for 'gammasurface_content'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    gamma : str
        Replacement parameter key name for 'gamma'.
    """
    
    # Set default keynames
    keynames = ['gammasurface_file', 'gammasurface_content', 'ucell', 'gamma']
    
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
        
    # Extract input values and assign default values
    gammasurface_file = input_dict.get(kwargs['gammasurface_file'], None)
    gammasurface_content = input_dict.get(kwargs['gammasurface_content'], None)
    ucell = input_dict.get(kwargs['ucell'], None)
    
    # Replace defect model with defect content if given
    if gammasurface_content is not None:
        gammasurface_file = gammasurface_content
    
    # If defect model is given
    if gammasurface_file is not None:
        pass
    
    else:
        raise ValueError('gammasurface_file is required')
    
    # Get ucell's box
    if ucell is not None:
        box = ucell.box
    else:
        box = am.Box()
    
    if build is True:
        gamma = am.defect.GammaSurface(model=gammasurface_file, box=box)
    else:
        gamma = None
    
    input_dict['gamma'] = gamma