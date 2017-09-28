from __future__ import division, absolute_import, print_function

from copy import deepcopy

import numpy as np
import atomman as am

def systemmanipulate(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with manupulating a ucell
    system to produce an initialsystem system.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'ucell'** unmodified system to manipulate
    - **'x_axis', 'y_axis', z_axis'** three orthogonal axes vectors by which
      to rotate.
    - **'atomshift'** scaled vector to shift all atoms by.
    - **'sizemults'** 3x2 array of ints indicating how to create a supercell.
    - **'axes'** a 3x3 array containing all three axis terms.
    - **'initialsystem'** the resulting system after manipulation is saved
      here.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    build : bool
        If False, parameters will be interpreted, but objects won't be built
        from them (Default is True).
    ucell : str
        Replacement parameter key name for 'ucell'.
    x_axis : str
        Replacement parameter key name for 'x_axis'.
    y_axis : str
        Replacement parameter key name for 'y_axis'.
    z_axis : str
        Replacement parameter key name for 'z_axis'.
    atomshift : str
        Replacement parameter key name for 'atomshift'.
    sizemults : str
        Replacement parameter key name for 'sizemults'.
    axes : str
        Replacement parameter key name for 'axes'.
    initialsystem : str
        Replacement parameter key name for 'initialsystem'.
    """
    
    #Set default keynames
    keynames = ['ucell', 'x_axis', 'y_axis', 'z_axis', 'axes', 'atomshift',
                'sizemults', 'initialsystem']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    x_axis = input_dict.get(kwargs['x_axis'], None)
    y_axis = input_dict.get(kwargs['y_axis'], None)
    z_axis = input_dict.get(kwargs['z_axis'], None)
    atomshift = input_dict.get(kwargs['atomshift'], '0 0 0')
    sizemults = input_dict.get(kwargs['sizemults'], '1 1 1')
    
    # Assign default axis values only if all are None
    if x_axis is None and y_axis is None and z_axis is None:
        x_axis = '1 0 0'
        y_axis = '0 1 0'
        z_axis = '0 0 1'
    
    # Issue error for incomplete axis set
    elif x_axis is None or y_axis is None or z_axis is None:
        raise TypeError('incomplete set of axis terms')
        
    # Convert string values to lists of numbers
    sizemults = list(np.array(sizemults.strip().split(), dtype=int))
    
    # Build axes from x_axis, y_axis and z_axis
    x = np.array(x_axis.strip().split(), dtype=float)
    y = np.array(y_axis.strip().split(), dtype=float)
    z = np.array(z_axis.strip().split(), dtype=float)
    axes = np.array([x, y, z])
    
    # Properly divide up sizemults if 6 terms given
    if len(sizemults) == 6:
        if (sizemults[0] <= 0 
            and sizemults[0] < sizemults[1]
            and sizemults[1] >= 0
            and sizemults[2] <= 0
            and sizemults[2] < sizemults[3]
            and sizemults[3] >= 0
            and sizemults[4] <= 0
            and sizemults[4] < sizemults[5]
            and sizemults[5] >= 0):
            
            sizemults =  [[sizemults[0], sizemults[1]],
                          [sizemults[2], sizemults[3]],
                          [sizemults[4], sizemults[5]]]
        
        else: 
            raise ValueError('Invalid sizemults command')
            
    # Properly divide up sizemults if 3 terms given
    elif len(sizemults) == 3:
        for i in xrange(3):
            
            # Add 0 before if value is positive
            if sizemults[i] > 0:
                sizemults[i] = [0, sizemults[i]]
            
            # Add 0 after if value is negative
            elif sizemults[i] < 0:
                sizemults[i] = [sizemults[i], 0]
            
            else: 
                raise ValueError('Invalid sizemults command')
        
    else: 
        raise ValueError('Invalid sizemults command')
    
    # Build initialsystem
    if build is True:
        # Extract ucell
        ucell = input_dict[kwargs['ucell']]
        
        # Copy ucell to initialsystem
        initialsystem = deepcopy(ucell)

        # Rotate to specified axes
        try:
            initialsystem = am.rotate_cubic(initialsystem, axes)
        except:
            if not np.allclose(axes, np.array([[1,0,0], [0,1,0], [0,0,1]])):
                raise ValueError('Rotation of non-cubic systems not supported yet')

        # Shift atoms by atomshift
        shift = list(np.array(atomshift.strip().split(), dtype=float))
        shift = (shift[0] * initialsystem.box.avect +
                 shift[1] * initialsystem.box.bvect +
                 shift[2] * initialsystem.box.cvect)
        pos = initialsystem.atoms_prop(key='pos')
        initialsystem.atoms_prop(key='pos', value=pos+shift)

        # Apply sizemults
        initialsystem.supersize(tuple(sizemults[0]), tuple(sizemults[1]),
                                tuple(sizemults[2]))
    
    else:
        initialsystem = None
     
    # Save processed terms
    input_dict[kwargs['x_axis']] = x_axis
    input_dict[kwargs['y_axis']] = y_axis
    input_dict[kwargs['z_axis']] = z_axis
    input_dict[kwargs['atomshift']] = atomshift
    input_dict[kwargs['sizemults']] = sizemults
    input_dict[kwargs['axes']] = axes
    input_dict[kwargs['initialsystem']] = initialsystem