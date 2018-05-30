# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am

__all__ = ['stackingfaultpart2']

def stackingfaultpart2(input_dict, build=True, **kwargs):
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
    - **'uvws'** a 3x3 array containing all three uvw terms.
    - **'faultpos'** the absolute fault position relative to the initial
      system.
    - **'shiftvector1'** one of the two fault shifting vectors as a Cartesian
      vector.
    - **'shiftvector2'** one of the two fault shifting vectors as a Cartesian
      vector.
    - **'transformationmatrix'** The Cartesian transformation matrix associated
      with changing from ucell to initialsystem
    
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
    uvws : str
        Replacement parameter key name for 'uvws'.
    faultpos : str
        Replacement parameter key name for 'faultpos'.
    shiftvector1 : str
        Replacement parameter key name for 'shiftvector1'.
    shiftvector2 : str
        Replacement parameter key name for 'shiftvector2'.
    transformationmatrix : str
        Replacement parameter key name for 'transformationmatrix'.
    """
    
    # Set default keynames
    keynames = ['stackingfault_faultpos', 'stackingfault_shiftvector1',
                'stackingfault_shiftvector2', 'stackingfault_cutboxvector',
                'sizemults', 'ucell', 'uvws', 'faultpos', 'shiftvector1',
                'shiftvector2', 'transformationmatrix']
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
        transform = input_dict[kwargs['transformationmatrix']]
        
        # Convert string terms to arrays
        stackingfault_shiftvector1 = np.array(stackingfault_shiftvector1.strip().split(),
                                              dtype=float)
        stackingfault_shiftvector2 = np.array(stackingfault_shiftvector2.strip().split(),
                                              dtype=float)
        
        # Convert shift vectors from crystallographic to Cartesian vectors
        shiftvector1 = ucell.box.vects.T.dot(stackingfault_shiftvector1)
        shiftvector2 = ucell.box.vects.T.dot(stackingfault_shiftvector2)
        
        # Transform shift vectors
        shiftvector1 = transform.dot(shiftvector1)
        shiftvector1[np.isclose(shiftvector1, 0.0, atol=1e-10, rtol=0.0)] = 0.0
        shiftvector2 = transform.dot(shiftvector2)
        shiftvector2[np.isclose(shiftvector2, 0.0, atol=1e-10, rtol=0.0)] = 0.0
        
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