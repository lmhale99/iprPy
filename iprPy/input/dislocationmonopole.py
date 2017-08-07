from __future__ import division, absolute_import, print_function

import numpy as np

from DataModelDict import DataModelDict as DM

def dislocationmonopole(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with a dislocation-monopole
    record.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'dislocation_model'** a dislocation-monopole record to load.
    - **'dislocation_content'** alternate file or content to load instead of
      specified dislocation_model.  This is used by prepare functions.
    - **'x_axis', 'y_axis', 'z_axis'** the orientation axes.  This function
      only reads in values from the dislocation_model.
    - **'atomshift'** the atomic shift to apply to all atoms.  This function
      only reads in values from the dislocation_model.
    - **'dislocation_burgersvector'** the dislocation's Burgers vector as a
      crystallographic.vector.
    - **'dislocation_boundaryshape'** defines the shape of the boundary
      region.
    - **'dislocation_boundarywidth'** defines the minimum width of the
      boundary region.  This term is in units of the unit cell's a lattice
      parameter.
    - **'ucell'** the unit cell system. Used here in scaling the model
      parameters to the system being explored.
    - **'burgersvector'** the dislocation's Burgers vector as a Cartesian
      vector.
    - **'boundarywidth'** defines the minimum width of the boundary region.
      This term is in length units.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    dislocation_model : str
        Replacement parameter key name for 'dislocation_model'.
    dislocation_content : str
        Replacement parameter key name for 'dislocation_content'.
    x_axis : str
        Replacement parameter key name for 'x_axis'.
    y_axis : str
        Replacement parameter key name for 'y_axis'.
    z_axis : str
        Replacement parameter key name for 'z_axis'.
    atomshift : str
        Replacement parameter key name for 'atomshift'.
    dislocation_burgersvector : str
        Replacement parameter key name for 'dislocation_burgersvector'.
    dislocation_boundaryshape : str
        Replacement parameter key name for 'dislocation_boundaryshape'.
    dislocation_boundarywidth : str
        Replacement parameter key name for 'dislocation_boundarywidth'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    burgersvector : str
        Replacement parameter key name for 'burgersvector'.
    boundarywidth : str
        Replacement parameter key name for 'boundarywidth'.
    """
    
    # Set default keynames
    keynames = ['dislocation_model', 'dislocation_content', 'x_axis',
                'y_axis', 'z_axis', 'atomshift', 'dislocation_burgersvector',
                'dislocation_boundaryshape', 'dislocation_boundarywidth',
                'ucell', 'burgersvector', 'boundarywidth']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    dislocation_model = input_dict.get(kwargs['dislocation_model'], None)
    dislocation_content = input_dict.get(kwargs['dislocation_content'], None)
    dislocation_boundaryshape = input_dict.get(kwargs['dislocation_boundaryshape'], 'circle')
    dislocation_boundarywidth = float(input_dict.get(kwargs['dislocation_boundarywidth'], 3.0))
    ucell = input_dict.get(kwargs['ucell'], None)
    
    # Replace defect model with defect content if given
    if dislocation_content is not None:
        dislocation_model = dislocation_content
    
    # If defect model is given
    if dislocation_model is not None:
        
        # Verify competing parameters are not defined
        for key in ('atomshift', 'x_axis', 'y_axis', 'z_axis', 
                    'dislocation_burgersvector'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '
                                                   + kwargs['dislocation_model']
                                                   + ' cannot both be supplied')
        
        # Load defect model
        dislocation_model = DM(dislocation_model).find('dislocation-monopole')
            
        # Extract parameter values from defect model
        input_dict[kwargs['x_axis']] = dislocation_model['calculation-parameter']['x_axis']
        input_dict[kwargs['y_axis']] = dislocation_model['calculation-parameter']['y_axis']
        input_dict[kwargs['z_axis']] = dislocation_model['calculation-parameter']['z_axis']
        input_dict[kwargs['atomshift']] = dislocation_model['calculation-parameter']['atomshift']
        input_dict[kwargs['dislocation_burgersvector']] = dislocation_model['calculation-parameter']['burgersvector']
    
    # Set default parameter values if defect model not given
    #else: 
    
    # convert parameters if ucell exists
    if ucell is not None:
        dislocation_burgersvector = input_dict[kwargs['dislocation_burgersvector']]
        dislocation_burgersvector = np.array(dislocation_burgersvector.strip().split(),
                                             dtype=float)
        
        # Convert crystallographic vectors to Cartesian vectors
        burgersvector = (dislocation_burgersvector[0] * ucell.box.avect +
                         dislocation_burgersvector[1] * ucell.box.bvect +
                         dislocation_burgersvector[2] * ucell.box.cvect)
        
        # Scale boundary width by unit cell's a lattice constant
        boundarywidth = ucell.box.a * dislocation_boundarywidth
        
    else:
        burgersvector = None
        boundarywidth = None
        
    # Save processed terms
    input_dict[kwargs['dislocation_model']] = dislocation_model
    input_dict[kwargs['dislocation_boundaryshape']] = dislocation_boundaryshape
    input_dict[kwargs['dislocation_boundarywidth']] = dislocation_boundarywidth
    input_dict[kwargs['burgersvector']] = burgersvector
    input_dict[kwargs['boundarywidth']] = boundarywidth
    