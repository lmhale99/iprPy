from copy import deepcopy

import numpy as np
import atomman as am
import atomman.lammps as lmp

from .sizemults import sizemults

def system_manipulate(input_dict, **kwargs):
    """
    Handles input parameters associated with manipulating a system.
    1. Takes the 'ucell' unit cell system.
    2. Sets default values to 'x_axis', 'y_axis', and 'z_axis' if needed.
    3. Sets default value of '0 0 0' to 'atomshift' term if needed.
    4. Sets default value of '1 1 1' to 'sizemults' term if needed.
    5. Applies rotation specified by axes terms, shifts all atoms by 
      'atomshift' and supersizes by 'sizemults' to 'ucell'. The resulting
      system is saved to the 'initialsystem' term.
       
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
    
    #Give default values for terms
    if kwargs['x_axis'] in input_dict or kwargs['y_axis'] in input_dict or kwargs['z_axis'] in input_dict:
        if kwargs['x_axis'] not in input_dict or kwargs['y_axis'] not in input_dict or kwargs['z_axis'] not in input_dict:
            raise TypeError('incomplete set of axis terms found')
    else:
        input_dict[kwargs['x_axis']] = '1 0 0'
        input_dict[kwargs['y_axis']] = '0 1 0'
        input_dict[kwargs['z_axis']] = '0 0 1'
    input_dict[kwargs['atomshift']] = input_dict.get(kwargs['atomshift'], '0 0 0')   
    input_dict[kwargs['sizemults']] = input_dict.get(kwargs['sizemults'], '1 1 1')

    #Convert strings to number lists
    if isinstance(input_dict[kwargs['x_axis']], (str, unicode)): 
        input_dict[kwargs['x_axis']] = list(np.array(input_dict[kwargs['x_axis']].strip().split(), dtype=float))
    if isinstance(input_dict[kwargs['y_axis']], (str, unicode)): 
        input_dict[kwargs['y_axis']] = list(np.array(input_dict[kwargs['y_axis']].strip().split(), dtype=float))
    if isinstance(input_dict[kwargs['z_axis']], (str, unicode)):
        input_dict[kwargs['z_axis']] = list(np.array(input_dict[kwargs['z_axis']].strip().split(), dtype=float))
    if isinstance(input_dict[kwargs['atomshift']], (str, unicode)): 
        input_dict[kwargs['atomshift']] = list(np.array(input_dict[kwargs['atomshift']].strip().split(), dtype=float))
    
    #Interpret sizemults
    input_dict[kwargs['sizemults']] = sizemults(input_dict)
        
    #copy ucell to initialsystem
    input_dict[kwargs['initialsystem']] = deepcopy(input_dict[kwargs['ucell']])
    
    #Build axes from x-axis, y-axis and z-axis
    axes = np.array([input_dict[kwargs['x_axis']], input_dict[kwargs['y_axis']], input_dict[kwargs['z_axis']]])

    #Rotate using axes
    try: input_dict[kwargs['initialsystem']] = am.rotate_cubic(input_dict[kwargs['initialsystem']], axes)
    except: input_dict[kwargs['initialsystem']] = lmp.normalize(am.rotate(input_dict[kwargs['initialsystem']], axes))
        
    #apply atomshift
    shift = (input_dict[kwargs['atomshift']][0] * input_dict[kwargs['initialsystem']].box.avect +
             input_dict[kwargs['atomshift']][1] * input_dict[kwargs['initialsystem']].box.bvect +
             input_dict[kwargs['atomshift']][2] * input_dict[kwargs['initialsystem']].box.cvect)
    pos = input_dict[kwargs['initialsystem']].atoms_prop(key='pos')
    input_dict[kwargs['initialsystem']].atoms_prop(key='pos', value=pos+shift)
   
    #apply sizemults
    input_dict[kwargs['initialsystem']].supersize(tuple(input_dict[kwargs['sizemults']][0]), tuple(input_dict[kwargs['sizemults']][1]), tuple(input_dict[kwargs['sizemults']][2]))