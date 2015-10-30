import iprp
import numpy as np

              

#Reads a LAMMPS style atom input file and returns a iprp.System. 
#Periodic boundary information and atomtypes need to be supplied. 
def read_atom(fname, atomtypes, pbc, style='atomic'):
    with open(fname, 'r') as fin:
        readtime = False
        readmass = False
        count = 0
        box = np.zeros((3, 3))
        
        #loop over all lines in file
        for line in fin:
            terms = line.split()
            if len(terms)>0:
                
                #read atomic information if time to do so
                if readtime == True:
                    id = int(terms[idindex])-1
                    for i in xrange(len(terms)):
                        if prop_names[i] != 'id':
                            atoms[id].set(prop_names[i], terms[i])
                    count += 1
                    if count == natoms:
                        readtime = False
                        count = 0
                
                #if readmass == True:
                #    masses = [0 for i in xrange(ntypes)]
                #    masses[int(terms[0])-1] = float(terms[1])
                #    count +=1
                #    if count == ntypes:
                #        readmass = False
                #        count = 0                

                #read number of atoms 
                elif len(terms) == 2 and terms[1] == 'atoms':
                    natoms = int(terms[0])
                    atoms = [iprp.Atom(1, np.zeros(3)) for i in xrange(natoms)]
                
                #read number of atom types
                elif len(terms) == 3 and terms[1] == 'atom' and terms[2] == 'types': 
                    ntypes = int(terms[0])
                    if len(atomtypes) != ntypes:
                        raise ValueError('Wrong number of atom types!')
                    #masses = []
                
                #read boundary info
                elif len(terms) == 4 and terms[2] == 'xlo' and terms[3] == 'xhi':
                    box[0,0] = float(terms[0])
                    box[0,1] = float(terms[1])
                elif len(terms) == 4 and terms[2] == 'ylo' and terms[3] == 'yhi':
                    box[1,0] = float(terms[0])
                    box[1,1] = float(terms[1])
                elif len(terms) == 4 and terms[2] == 'zlo' and terms[3] == 'zhi':
                    box[2,0] = float(terms[0])
                    box[2,1] = float(terms[1]) 
                elif len(terms) == 6 and terms[3] == 'xy' and terms[4] == 'xz' and terms[5] == 'yz':
                    box[0,2] = float(terms[0])
                    box[1,2] = float(terms[1])   
                    box[2,2] = float(terms[2])
                
                #Flag when reached data and setup for reading
                elif len(terms) == 1:
                    if terms[0] == 'Atoms':
                        prop_names = atom_style_params(style)
                        idindex = prop_names.index('id')
                        readtime = True
                    #elif terms[0] == 'Masses':
                    #    readmass = True
                    elif terms[0] == 'Velocities':
                        if style == 'electron':
                            prop_names = ['id','vx','vy','vz','ervel']
                        elif style == 'sphere':
                            prop_names = ['id','vx','vy','vz','wx','wy','wz']
                        else:
                            prop_names = ['id','vx','vy','vz']
                        idindex = prop_names.index('id')
                        readtime = True
                        
    return iprp.System(atoms=atoms, atomtypes=atomtypes, box=box, pbc=pbc)                
            

#Specifies the per-atom values associated with the different LAMMPS atom_style options    
def atom_style_params(style='atomic'):
    if style == 'angle':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']
    elif style == 'atomic':
        params = ['id', 'type', 'x', 'y', 'z']
    elif style == 'bond':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']       
    elif style == 'charge':
        params = ['id', 'type', 'q', 'x', 'y', 'z']
    elif style == 'dipole':
        params = ['id', 'type', 'q', 'x', 'y', 'z', 'mux', 'muy', 'muz']
    elif style == 'electron':
        params = ['id', 'type', 'q', 'spin', 'eradius', 'x', 'y', 'z']
    elif style == 'full':
        params = ['id', 'mol', 'type', 'q', 'x', 'y', 'z']
    elif style == 'meso':
        params = ['id', 'type', 'rho', 'e', 'cv', 'x', 'y', 'z']
    elif style == 'molecular':
        params = ['id', 'mol', 'type', 'x', 'y', 'z']
    elif style == 'peri':
        params = ['id', 'type', 'volume', 'density', 'x', 'y', 'z']
    elif style == 'sphere':
        params = ['id', 'type', 'diameter', 'density', 'x', 'y', 'z']
    elif style == 'template':
        params = ['id', 'mol', 'template-index', 'template-atom', 'type', 'x', 'y', 'z']
    elif style == 'wavepacket':
        params = ['id', 'type', 'q', 'spin', 'eradius', 'etag', 'cs_re', 'cs_im', 'x', 'y', 'z']
    else:
        raise ValueError('atom_style ' + style + ' not supported')
    
    return params

#Writes a LAMMPS style atom file from sys using supplied atom style    
def write_atom(fname, sys, style='atomic'):
    #Header info
    f = open(fname,'w')
    f.write('\n%i atoms\n'%sys.natoms())
    f.write('%i atom types\n'%sys.ntypes())
    f.write(str(sys.box[0,0]) + ' ' + str(sys.box[0,1]) + ' xlo xhi\n')
    f.write(str(sys.box[1,0]) + ' ' + str(sys.box[1,1]) + ' ylo yhi\n')
    f.write(str(sys.box[2,0]) + ' ' + str(sys.box[2,1]) + ' zlo zhi\n')
    if sys.box[0,2] > 0.0 or sys.box[1,2] > 0.0 or sys.box[2,2] > 0.0:
        f.write(str(sys.box[0,2]) + ' ' + str(sys.box[1,2]) + ' ' + str(sys.box[2,2]) + ' xy xz yz\n')
    
    #Atomic info
    prop_names = atom_style_params(style=style)
    f.write('\nAtoms\n\n')
    for i in xrange(sys.natoms()):
        line = ''
        for prop in prop_names:
            if prop == 'id':
                line += '%i' %(i+1)
            elif prop == 'type':
                line += ' %i' %(sys.atoms[i].get(prop))
            else:
                line += ' %.13e' %(sys.atoms[i].get(prop))
        f.write(line+'\n')
        
    #Velocity info
    #For later
    
    f.close()

#Writes a LAMMPS style dump file from sys using all assigned per-atom properties    
def write_dump(fname, sys):
    f = open(fname,'w')
    f.write('ITEM: TIMESTEP\n')
    f.write('0\n')
    f.write('ITEM: NUMBER OF ATOMS\n')
    f.write('%i\n' %(sys.natoms()))
    if sys.box[0,2] > 0.0 or sys.box[1,2] > 0.0 or sys.box[2,2] > 0.0:
        f.write('ITEM: BOX BOUNDS xy xz yz')
        for i in xrange(3):
            if sys.pbc[i]:
                f.write(' pp')
            else:
                f.write(' ss')
        f.write('\n')
        for i in xrange(3):
            f.write(str(sys.box[i,0]) + ' ' + str(sys.box[i,1]) + ' ' + str(sys.box[i,2]) + '\n')
    else:
        f.write('ITEM: BOX BOUNDS')
        for i in xrange(3):
            if sys.pbc[i]:
                f.write(' pp')
            else:
                f.write(' ss')
        f.write('\n')
        for i in xrange(3):
            f.write(str(sys.box[i,0]) + ' ' + str(sys.box[i,1]) + '\n')
    
    prop_list = sys.atoms[0].list()
    f.write('ITEM: ATOMS id')
    for property in prop_list:
        f.write(' ' + property)
    f.write('\n')
    for i in xrange(sys.natoms()):
        f.write('%i '%(i+1))
        for property in prop_list:
            if isinstance(sys.atoms[i].get(property), int):
                f.write(' %i' %sys.atoms[i].get(property))
            else:
                f.write(' %.14e' %sys.atoms[i].get(property))
        f.write('\n')

    f.close()

#Take LAMMPS screen output and parse out the thermo data into a list
def extract(output):
    thermo = False
    first = True
    thermolist = []
    
    lines = output.split('\n')
    for line in lines:
        terms = line.split()
        
        #If the line has terms
        if len(terms)>0:
            #If the line starts with Step, then set thermo
            if terms[0] == 'Step':
                thermo = True
                #Make the first line of the returned array the thermo data headers
                if first:
                    thermolist.append(terms)
                    first = False
                    
            #If thermo has been set, the lines probably contain data
            elif thermo:
                #Check that the first term is an integer
                if terms[0].isdigit():
                    thermolist.append(terms)                   
                else:
                    thermo = False                    

    return thermolist     