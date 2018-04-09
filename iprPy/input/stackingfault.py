# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am

def stackingfault1(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with a stacking-fault record.
    This function should be called before iprPy.input.systemmanupulate.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'stackingfault_model'** a stacking-fault record to load.
    - **'stackingfault_content'** alternate file or content to load instead of
      specified stackingfault_model.  This is used by prepare functions.
    - **'x_axis, y_axis, z_axis'** the orientation axes.  This function only
      reads in values from the stackingfault_model.
    - **'atomshift'** the atomic shift to apply to all atoms.  This function
      only reads in values from the stackingfault_model.
    - **'stackingfault_cutboxvector'** the cutboxvector parameter for the
      stackingfault model.  Default value is 'c' if neither
      stackingfault_model nor stackingfault_cutboxvector are given.
    - **'stackingfault_faultpos'** the relative position within a unit cell
      where the stackingfault is to be placed.
    - **'stackingfault_shiftvector1'** one of the two fault shifting vectors
      as a crystallographic vector.
    - **'stackingfault_shiftvector2'** one of the two fault shifting vectors
      as a crystallographic vector.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    stackingfault_model : str
        Replacement parameter key name for 'stackingfault_model'.
    stackingfault_content : str
        Replacement parameter key name for 'stackingfault_content'.
    x_axis : str
        Replacement parameter key name for 'x_axis'.
    y_axis : str
        Replacement parameter key name for 'y_axis'.
    z_axis : str
        Replacement parameter key name for 'z_axis'.
    atomshift : str
        Replacement parameter key name for 'atomshift'.
    stackingfault_cutboxvector : str
        Replacement parameter key name for 'stackingfault_cutboxvector'.
    stackingfault_faultpos : str
        Replacement parameter key name for 'stackingfault_faultpos'.
    stackingfault_shiftvector1 : str
        Replacement parameter key name for 'stackingfault_shiftvector1'.
    stackingfault_shiftvector2 : str
        Replacement parameter key name for 'stackingfault_shiftvector2'.
    """
    
    # Set default keynames
    keynames = ['stackingfault_model', 'stackingfault_content', 'x_axis',
                'y_axis', 'z_axis', 'atomshift', 'stackingfault_cutboxvector',
                'stackingfault_faultpos', 'stackingfault_shiftvector1',
                'stackingfault_shiftvector2']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    stackingfault_model = input_dict.get(kwargs['stackingfault_model'], None)
    stackingfault_content = input_dict.get(kwargs['stackingfault_content'],
                                           None)
    
    # Replace defect model with defect content if given
    if stackingfault_content is not None:
        stackingfault_model = stackingfault_content
    
    # If defect model is given
    if stackingfault_model is not None:
        
        # Verify competing parameters are not defined
        for key in ('atomshift', 'x_axis', 'y_axis', 'z_axis',
                    'stackingfault_cutboxvector', 'stackingfault_faultpos',
                    'stackingfault_shiftvector1',
                    'stackingfault_shiftvector2'):
            assert kwargs[key] not in input_dict, (kwargs[key] + ' and '
                                                   + kwargs['dislocation_model']
                                                   + ' cannot both be supplied')
        
        # Load defect model
        stackingfault_model = DM(stackingfault_model).find('stacking-fault')
            
        # Extract parameter values from defect model
        input_dict[kwargs['x_axis']] = stackingfault_model['calculation-parameter']['x_axis']
        input_dict[kwargs['y_axis']] = stackingfault_model['calculation-parameter']['y_axis']
        input_dict[kwargs['z_axis']] = stackingfault_model['calculation-parameter']['z_axis']
        input_dict[kwargs['atomshift']] = stackingfault_model['calculation-parameter']['atomshift']
        input_dict[kwargs['stackingfault_cutboxvector']] = stackingfault_model['calculation-parameter']['cutboxvector']
        input_dict[kwargs['stackingfault_faultpos']] = float(stackingfault_model['calculation-parameter']['faultpos'])
        input_dict[kwargs['stackingfault_shiftvector1']] = stackingfault_model['calculation-parameter']['shiftvector1']
        input_dict[kwargs['stackingfault_shiftvector2']] = stackingfault_model['calculation-parameter']['shiftvector2']
    
    # Set default parameter values if defect model not given
    else:
        input_dict[kwargs['stackingfault_cutboxvector']] = input_dict.get(kwargs['stackingfault_cutboxvector'], 'c')
        input_dict[kwargs['stackingfault_faultpos']] = float(input_dict.get(kwargs['stackingfault_faultpos'], 0.5))
        assert input_dict[kwargs['stackingfault_cutboxvector']] in ['a', 'b', 'c'], 'invalid stackingfault_cutboxvector'
        
    # Save processed terms
    input_dict[kwargs['stackingfault_model']] = stackingfault_model

def stackingfault2(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with a stacking-fault record.
    This function should be called after iprPy.input.systemmanupulate.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    
    - **'stackingfault_faultpos'** the relative position within a unit cell
      where the stackingfault is to be placed.
    - **'stackingfault_shiftvector1'** one of the two fault shifting vectors
      as a crystallographic vector.
    - **'stackingfault_shiftvector2'** one of the two fault shifting vectors
      as a crystallographic vector.
    - **'sizemults'** the system size multipliers. Only accessed here.
    - **'ucell'** the unit cell system. Only accessed here.
    - **'axes'** the 3x3 matrix of axes. Only accessed here.
    - **'faultpos'** the absolute fault position relative to the initial
      system.
    - **'shiftvector1'** one of the two fault shifting vectors as a Cartesian
      vector.
    - **'shiftvector2'** one of the two fault shifting vectors as a Cartesian
      vector.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    stackingfault_faultpos : str
        Replacement parameter key name for 'stackingfault_faultpos'.
    stackingfault_shiftvector1 : str
        Replacement parameter key name for 'stackingfault_shiftvector1'.
    stackingfault_shiftvector2 : str
        Replacement parameter key name for 'stackingfault_shiftvector2'.
    sizemults : str
        Replacement parameter key name for 'sizemults'.
    ucell : str
        Replacement parameter key name for 'ucell'.
    axes : str
        Replacement parameter key name for 'axes'.
    faultpos : str
        Replacement parameter key name for 'faultpos'.
    shiftvector1 : str
        Replacement parameter key name for 'shiftvector1'.
    shiftvector2 : str
        Replacement parameter key name for 'shiftvector2'.
    """
    
    # Set default keynames
    keynames = ['stackingfault_faultpos', 'stackingfault_shiftvector1',
                'stackingfault_shiftvector2', 'stackingfault_cutboxvector',
                'sizemults', 'ucell', 'axes', 'faultpos', 'shiftvector1',
                'shiftvector2']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    if build is True:
        
        # Extract input values and assign default values
        stackingfault_faultpos = input_dict[kwargs['stackingfault_faultpos']]
        stackingfault_shiftvector1 = input_dict[kwargs['stackingfault_shiftvector1']]
        stackingfault_shiftvector2 = input_dict[kwargs['stackingfault_shiftvector2']]
        stackingfault_cutboxvector = input_dict[kwargs['stackingfault_cutboxvector']]
        sizemults = input_dict[kwargs['sizemults']]
        ucell = input_dict[kwargs['ucell']]
        axes = input_dict[kwargs['axes']]
        
        # Convert string terms to arrays
        stackingfault_shiftvector1 = np.array(stackingfault_shiftvector1.strip().split(),
                                              dtype=float)
        stackingfault_shiftvector2 = np.array(stackingfault_shiftvector2.strip().split(),
                                              dtype=float)
        
        # Convert crystallographic vectors to Cartesian vectors
        shiftvector1 = (stackingfault_shiftvector1[0] * ucell.box.avect +
                        stackingfault_shiftvector1[1] * ucell.box.bvect +
                        stackingfault_shiftvector1[2] * ucell.box.cvect)
        
        shiftvector2 = (stackingfault_shiftvector2[0] * ucell.box.avect +
                        stackingfault_shiftvector2[1] * ucell.box.bvect +
                        stackingfault_shiftvector2[2] * ucell.box.cvect)
        
        # Transform using axes
        T = am.tools.axes_check(axes)
        shiftvector1 = T.dot(shiftvector1)
        shiftvector2 = T.dot(shiftvector2)

        # Identify number of size multiples, m, along cutboxvector
        if   stackingfault_cutboxvector == 'a': 
            m = sizemults[0]
        elif stackingfault_cutboxvector == 'b': 
            m = sizemults[1]
        elif stackingfault_cutboxvector == 'c': 
            m = sizemults[2]
         
        if isinstance(m, (list, tuple)):
            m = m[1] - m[0]
        
        # For odd m, initial position of 0.5 goes to 0.5
        if m % 2 == 1:
            faultpos = (stackingfault_faultpos + (m-1) * 0.5) / m
        # For even m, initial position of 0.0 goes to 0.5
        else:
            faultpos = (2 * stackingfault_faultpos + m) / (2 * m)
    
    else:
        faultpos = None
        shiftvector1 = None
        shiftvector2 = None
    
    # Save processed terms
    input_dict[kwargs['faultpos']] = faultpos
    input_dict[kwargs['shiftvector1']] = shiftvector1
    input_dict[kwargs['shiftvector2']] = shiftvector2