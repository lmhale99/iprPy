# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

__all__ = ['freesurface']

def freesurface(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with a free-surface record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'surface_file'** a free-surface record to load.
    - **'surface_content'** alternate file or content to load instead of
      specified surface_model. This is used by prepare functions.
    - **'surface_model'** the open DataModelDict of file/content.
    - **'a_uvw, b_uvw, c_uvw'** the orientation [uvw] indices. This function only
      reads in values from the surface_model.
    - **'atomshift'** the atomic shift to apply to all atoms. This function
      only reads in values from the surface_model.
    - **'surface_cutboxvector'** the cutboxvector parameter for the surface
      model. Default value is 'c' if neither surface_model nor 
      surface_cutboxvector are given.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    surface_file : str
        Replacement parameter key name for 'surface_file'.
    surface_content : str
        Replacement parameter key name for 'surface_content'.
    surface_model : str
        Replacement parameter key name for 'surface_model'.
    a_uvw : str
        Replacement parameter key name for 'a_uvw'.
    b_uvw : str
        Replacement parameter key name for 'b_uvw'.
    c_uvw : str
        Replacement parameter key name for 'c_uvw'.
    atomshift : str
        Replacement parameter key name for 'atomshift'.
    surface_cutboxvector : str
        Replacement parameter key name for 'surface_cutboxvector'.
    """
    
    # Set default keynames
    keynames = ['surface_file', 'surface_content', 'surface_model', 
                'a_uvw', 'b_uvw', 'c_uvw', 'atomshift', 'surface_cutboxvector']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    surface_file = input_dict.get(kwargs['surface_file'], None)
    surface_content = input_dict.get(kwargs['surface_content'], None)
    
    # Replace defect model with defect content if given
    if surface_content is not None:
        surface_file = surface_content
    
    # If defect model is given
    if surface_file is not None:
        
        # Verify competing parameters are not defined
        for key in ('atomshift', 'a_uvw', 'b_uvw', 'c_uvw', 
                    'surface_cutboxvector'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '
                                                   + kwargs['dislocation_model']
                                                   + ' cannot both be supplied')
        
        # Load defect model
        surface_model = DM(surface_file).find('free-surface')
            
        # Extract parameter values from defect model
        input_dict[kwargs['a_uvw']] = surface_model['calculation-parameter']['a_uvw']
        input_dict[kwargs['b_uvw']] = surface_model['calculation-parameter']['b_uvw']
        input_dict[kwargs['c_uvw']] = surface_model['calculation-parameter']['c_uvw']
        input_dict[kwargs['atomshift']] = surface_model['calculation-parameter']['atomshift']
        input_dict[kwargs['surface_cutboxvector']] = surface_model['calculation-parameter']['cutboxvector']
    
    # Set default parameter values if defect model not given
    else:
        input_dict[kwargs['surface_cutboxvector']] = input_dict.get(kwargs['surface_cutboxvector'], 'c')
        assert input_dict[kwargs['surface_cutboxvector']] in ['a', 'b', 'c'], 'invalid surface_cutboxvector'
        
    # Save processed terms
    input_dict[kwargs['surface_model']] = surface_model