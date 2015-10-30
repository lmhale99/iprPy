from copy import deepcopy

#Modify the box size and atom types to support the boundary conditions for disl_relax_script
def boundaryfix(sys, b_width, shape):
    new = deepcopy(sys)
    ntypes = sys.ntypes()        
        
    #Extend box in x and y directions if needed
    for atom in new.atoms:
        if atom.get('x') < new.box[0,0]:
            new.box[0,0] = atom.get('x') - 0.01
        elif atom.get('x') > new.box[0,1]:
            new.box[0,1] = atom.get('x') + 0.01
        if atom.get('y') < new.box[1,0]:
            new.box[1,0] = atom.get('y') - 0.01
        elif atom.get('y') > new.box[1,1]:
            new.box[1,1] = atom.get('y') + 0.01
    
    if shape == 'circle':
        radius = abs(new.box[:2,:2]).min() #finds x or y bound closest to 0
        for atom in new.atoms:
            if (atom.get('x')**2 + atom.get('y')**2)**0.5 > radius - b_width:
                atom.set('type', atom.get('type') + ntypes)
    
    elif shape == 'rect':
        for atom in new.atoms:
            if atom.get('x') < new.box[0,0] + b_width or atom.get('x') > new.box[0,1] - b_width:
                atom.set('type', atom.get('type') + ntypes)
            elif atom.get('y') < new.box[1,0] + b_width or atom.get('y') > new.box[1,1] - b_width:
                aatom.set('type', atom.get('type') + ntypes)
    else:
        print 'Unknown shape type! Enter \'circle\' or \'rect\''

    #double the atomtypes
    atomtypes = deepcopy(sys.atomtypes)
    for at in sys.atomtypes:
        atomtypes.append(deepcopy(at))
    new.set('atomtypes',atomtypes)
        
    return new