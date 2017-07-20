from DataModelDict import DataModelDict as DM

def freesurface(input_dict, **kwargs):
    """
    Reads in calculation parameters associated with a free-surface record.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    surface_model -- a free-surface record to load.
    surface_content -- alternate file or content to load instead of specified 
                       surface_model. This is used by prepare functions.
    x_axis, y_axis, z_axis -- the orientation axes. This function only reads in
                              values from the surface_model.
    atomshift -- the atomic shift to apply to all atoms. This function only 
                 reads in values from the surface_model.
    surface_cutboxvector -- the cutboxvector parameter for the surface model. 
                            Default value is 'c' if neither surface_model nor 
                            surface_cutboxvector are given.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    surface_model -- replacement parameter key name for 'surface_model'
    surface_content -- replacement parameter key name for 'surface_content'
    x_axis -- replacement parameter key name for 'x_axis'
    y_axis -- replacement parameter key name for 'y_axis'
    z_axis -- replacement parameter key name for 'z_axis'
    atomshift -- replacement parameter key name for 'atomshift'
    surface_cutboxvector -- replacement parameter key name for 'surface_cutboxvector'
    
    """
    
    # Set default keynames
    keynames = ['surface_model', 'surface_content', 'x_axis', 'y_axis', 'z_axis', 
                'atomshift', 'surface_cutboxvector']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    surface_model =   input_dict.get(kwargs['surface_model'],   None)
    surface_content = input_dict.get(kwargs['surface_content'], None)
    
    # Replace defect model with defect content if given
    if surface_content is not None:
        surface_model = surface_content
    
    # If defect model is given
    if surface_model is not None:
        
        # Verify competing parameters are not defined
        for key in ('atomshift', 'x_axis', 'y_axis', 'z_axis', 'surface_cutboxvector'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '+ kwargs['dislocation_model'] + 
                                                   ' cannot both be supplied')
        
        # Load defect model
        surface_model = DM(surface_model).find('free-surface')
            
        # Extract parameter values from defect model
        input_dict[kwargs['x_axis']] = surface_model['calculation-parameter']['x_axis']
        input_dict[kwargs['y_axis']] = surface_model['calculation-parameter']['y_axis']
        input_dict[kwargs['z_axis']] = surface_model['calculation-parameter']['z_axis']
        input_dict[kwargs['atomshift']] = surface_model['calculation-parameter']['atomshift']
        input_dict[kwargs['surface_cutboxvector']] = surface_model['calculation-parameter']['cutboxvector']
    
    # Set default parameter values if defect model not given
    else:
        input_dict[kwargs['surface_cutboxvector']] = input_dict.get(kwargs['surface_cutboxvector'], 'c')
        assert input_dict[kwargs['surface_cutboxvector']] in ['a', 'b', 'c'], 'invalid surface_cutboxvector'
        
    # Save processed terms
    input_dict[kwargs['surface_model']] = surface_model