from copy import deepcopy

import numpy as np
import atomman as am
import atomman.lammps as lmp

from . import parse_size_mults

def system_manipulate(input_dict, ucell='ucell', x_axis='x-axis', y_axis='y-axis', 
                      z_axis='z-axis', atom_shift='atom_shift', 
                      size_mults='size_mults', initial_system='initial_system'):
    """
    Process input terms associated with manipulating a system.
    
    Arguments:
    input_dict -- dictionary of input terms to process.
    
    Keyword Arguments:
    ucell -- key in input_dict where the loaded base system is.
             Default value is 'ucell'.
    x_axis -- key in input_dict where the x-axis vector is stored.
              Default value is 'x-axis'.
    y_axis -- key in input_dict where the y-axis vector is stored.
              Default value is 'y-axis'.
    z_axis -- key in input_dict where the z-axis vector is stored.
              Default value is 'z-axis'.
    atom_shift -- key in input_dict where the atom_shift value is stored.
                  Default value is 'atom_shift'.
    size_mults -- key in input_dict where the size_mults term is stored.
                  Default value is 'size_mults'.
    initial_system -- key in input_dict where the resulting system will be saved.
                      Default value is 'initial_system'.
    """
    
    #Give default values for terms
    input_dict[x_axis] =     input_dict.get(x_axis,     '1 0 0')    
    input_dict[y_axis] =     input_dict.get(y_axis,     '0 1 0')
    input_dict[z_axis] =     input_dict.get(z_axis,     '0 0 1')
    input_dict[atom_shift] = input_dict.get(atom_shift, '0 0 0')   
    input_dict[size_mults] = input_dict.get(size_mults, '1 1 1')

    #Convert strings to number lists
    if isinstance(input_dict[x_axis], (str, unicode)): 
        input_dict[x_axis] = list(np.array(input_dict[x_axis].strip().split(), dtype=float))
    if isinstance(input_dict[y_axis], (str, unicode)): 
        input_dict[y_axis] = list(np.array(input_dict[y_axis].strip().split(), dtype=float))
    if isinstance(input_dict[z_axis], (str, unicode)):
        input_dict[z_axis] = list(np.array(input_dict[z_axis].strip().split(), dtype=float))
    if isinstance(input_dict[atom_shift], (str, unicode)): 
        input_dict[atom_shift] = list(np.array(input_dict[atom_shift].strip().split(), dtype=float))
    
    #Interpret size_mults
    input_dict[size_mults] = parse_size_mults(input_dict)
        
    #copy ucell to initial_system
    input_dict[initial_system] = deepcopy(input_dict[ucell])
    
    #Build axes from x-axis, y-axis and z-axis
    axes = np.array([input_dict[x_axis], input_dict[y_axis], input_dict[z_axis]])

    #Rotate using axes
    try: input_dict[initial_system] = am.rotate_cubic(input_dict[initial_system], axes)
    except: input_dict[initial_system] = lmp.normalize(am.rotate(input_dict[initial_system], axes))
        
    #apply atom_shift
    shift = (input_dict[atom_shift][0] * input_dict[initial_system].box.avect +
             input_dict[atom_shift][1] * input_dict[initial_system].box.bvect +
             input_dict[atom_shift][2] * input_dict[initial_system].box.cvect)
    pos = input_dict[initial_system].atoms_prop(key='pos')
    input_dict[initial_system].atoms_prop(key='pos', value=pos+shift)
   
    #apply size_mults
    input_dict[initial_system].supersize(tuple(input_dict[size_mults][0]), tuple(input_dict[size_mults][1]), tuple(input_dict[size_mults][2]))