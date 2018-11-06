# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am

# iprPy imports
from ...compatibility import range, int

__all__ = ['atomman_systemmanipulate']

def atomman_systemmanipulate(input_dict, build=True, **kwargs):
    """
    Interprets calculation parameters associated with manipulating a ucell
    system to produce an initialsystem system.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'ucell'** unmodified system to manipulate
    - **'a_uvw', 'b_uvw', c_uvw'** sets of [uvw] indices to rotate ucell to.
    - **'atomshift'** scaled vector to shift all atoms by.
    - **'sizemults'** 3x2 array of ints indicating how to create a supercell.
    - **'uvws'** a 3x3 array containing all three uvw terms.
    - **'transformationmatrix'** The Cartesian transformation matrix associated
      with changing from ucell to initialsystem
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
    a_uvw : str
        Replacement parameter key name for 'a_uvw'.
    b_uvw : str
        Replacement parameter key name for 'b_uvw'.
    c_uvw : str
        Replacement parameter key name for 'c_uvw'.
    atomshift : str
        Replacement parameter key name for 'atomshift'.
    sizemults : str
        Replacement parameter key name for 'sizemults'.
    uvws : str
        Replacement parameter key name for 'uvws'.
    transformationmatrix : str
        Replacement parameter key name for 'transformationmatrix'.
    initialsystem : str
        Replacement parameter key name for 'initialsystem'.
    """
    
    #Set default keynames
    keynames = ['ucell', 'a_uvw', 'b_uvw', 'c_uvw', 'uvws', 'atomshift',
                'sizemults', 'transformationmatrix', 'initialsystem']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    a_uvw = input_dict.get(kwargs['a_uvw'], None)
    b_uvw = input_dict.get(kwargs['b_uvw'], None)
    c_uvw = input_dict.get(kwargs['c_uvw'], None)
    atomshift = input_dict.get(kwargs['atomshift'], '0 0 0')
    sizemults = input_dict.get(kwargs['sizemults'], '1 1 1')
    
    # Assign default uvws only if all are None
    if a_uvw is None and b_uvw is None and c_uvw is None:
        a_uvw = '1 0 0'
        b_uvw = '0 1 0'
        c_uvw = '0 0 1'
    
    # Issue error for incomplete uvws set
    elif a_uvw is None or b_uvw is None or c_uvw is None:
        raise TypeError('incomplete set of uvws terms')
        
    # Convert string values to lists of numbers
    sizemults = sizemults.strip().split()
    for i in range(len(sizemults)):
        sizemults[i] = int(sizemults[i])
    
    # Build uvws from a_uvw, b_uvw and c_uvw
    a = np.array(a_uvw.strip().split(), dtype=float)
    b = np.array(b_uvw.strip().split(), dtype=float)
    c = np.array(c_uvw.strip().split(), dtype=float)
    uvws = np.array([a, b, c])
    
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
        for i in range(3):
            
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
        
        # Rotate to specified uvws
        initialsystem, transform = ucell.rotate(uvws, return_transform=True)
        
        # Shift atoms by atomshift
        shift = list(np.array(atomshift.strip().split(), dtype=float))
        shift = (shift[0] * initialsystem.box.avect +
                 shift[1] * initialsystem.box.bvect +
                 shift[2] * initialsystem.box.cvect)
        initialsystem.atoms.pos += shift
        
        # Apply sizemults
        initialsystem = initialsystem.supersize(tuple(sizemults[0]),
                                                tuple(sizemults[1]),
                                                tuple(sizemults[2]))
        initialsystem.wrap()
    
    else:
        initialsystem = None
        transform = None
    
    # Save processed terms
    input_dict[kwargs['a_uvw']] = a_uvw
    input_dict[kwargs['b_uvw']] = b_uvw
    input_dict[kwargs['c_uvw']] = c_uvw
    input_dict[kwargs['atomshift']] = atomshift
    input_dict[kwargs['sizemults']] = sizemults
    input_dict[kwargs['uvws']] = uvws
    input_dict[kwargs['transformationmatrix']] = transform
    input_dict[kwargs['initialsystem']] = initialsystem