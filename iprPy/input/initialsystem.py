from copy import deepcopy

import numpy as np
import atomman as am
import atomman.lammps as lmp

from .sizemults import sizemults

def initialsystem(input_dict, **kwargs):
    """
    Creates an initialsystem by manipulating a ucell system with the rotation 
    specified by axes terms, atomic shift specified by atomshift, and 
    system supersizing by sizemults.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    ucell -- unmodified system to manipulate
    x_axis, y_axis, z_axis -- three orthogonal axes vectors by which to rotate
    atomshift -- scaled vector to shift all atoms by
    sizemults -- 3x2 array of ints indicating how to create a supercell
    initialsystem -- the resulting system after manipulation is saved here
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    ucell -- replacement parameter key name for 'ucell'
    x_axis -- replacement parameter key name for 'x_axis'
    y_axis -- replacement parameter key name for 'y_axis'
    z_axis -- replacement parameter key name for 'z_axis'
    atomshift -- replacement parameter key name for 'atomshift'
    sizemults -- replacement parameter key name for 'sizemults'
    initialsystem -- replacement parameter key name for 'initialsystem'
    """   
    
    #Set default keynames
    keynames = ['ucell', 'x_axis', 'y_axis', 'z_axis', 
                'atomshift', 'sizemults', 'initialsystem']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #Check for ucell system
    assert kwargs['ucell'] in input_dict, kwargs['ucell'] + ' value not supplied'
        
    #copy ucell to initialsystem
    input_dict[kwargs['initialsystem']] = deepcopy(input_dict[kwargs['ucell']])
    
    #Build axes from x_axis, y_axis and z_axis
    axes = np.array([input_dict[kwargs['x_axis']], input_dict[kwargs['y_axis']], input_dict[kwargs['z_axis']]])

    #Rotate using axes
    try: 
        input_dict[kwargs['initialsystem']] = am.rotate_cubic(input_dict[kwargs['initialsystem']], axes)
    except: 
        input_dict[kwargs['initialsystem']] = lmp.normalize(am.rotate(input_dict[kwargs['initialsystem']], axes))
        
    #apply atomshift
    shift = (input_dict[kwargs['atomshift']][0] * input_dict[kwargs['initialsystem']].box.avect +
             input_dict[kwargs['atomshift']][1] * input_dict[kwargs['initialsystem']].box.bvect +
             input_dict[kwargs['atomshift']][2] * input_dict[kwargs['initialsystem']].box.cvect)
    pos = input_dict[kwargs['initialsystem']].atoms_prop(key='pos')
    input_dict[kwargs['initialsystem']].atoms_prop(key='pos', value=pos+shift)
   
    #apply sizemults
    input_dict[kwargs['initialsystem']].supersize(tuple(input_dict[kwargs['sizemults']][0]), tuple(input_dict[kwargs['sizemults']][1]), tuple(input_dict[kwargs['sizemults']][2]))