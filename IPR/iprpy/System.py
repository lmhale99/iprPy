from collections import OrderedDict
import numpy as np
from copy import deepcopy

from Atom import Atom
from Box import Box
from tools import mag
     
class System:
    #Define atomic system
    
    def __init__(self, atoms=[], box=Box(), pbc=(True, True, True), scale=False):
        #Initialize System instance
                
        assert isinstance(box, Box), 'Invalid box entry'
        self.__box = box
        
        assert len(pbc) == 3 and isinstance(pbc[0], bool) and isinstance(pbc[1], bool) and isinstance(pbc[2], bool), 'invalid pbc entry' 
        self.__pbc = tuple(pbc)
        
        self.atoms(atoms, scale=scale)
        self.__prop = {}
    
    def atoms(self, arg1=None, arg2=None, arg3=None, scale=False):
        #Get or set the atom list and atomic property values
        
        assert isinstance(scale, bool),             'scale must be True/False'
        
        #Return a copy of the atom list if no arguments (besides scale) given
        if arg1 is None and arg2 is None and arg3 is None:
            if scale:
                scaledatoms = []
                for atom in self.__atoms:
                    scaledatoms.append(self.scale(atom))
                return scaledatoms
            else:
                return deepcopy(self.__atoms)
                
        #Set atoms list if first argument is a list of Atoms
        elif isinstance(arg1, (list, tuple)):
            assert arg2 is None and arg3 is None,   'Invalid arguments: if first argument is a list only scale is allowed'
            if scale:
                self.__atoms = []
                for item in arg1:
                    assert isinstance(item, Atom),      'Invalid arguments: list is not a list of iprPy.Atoms'
                    self.__atoms.append(self.unscale(item))
            else:
                for item in arg1:
                    assert isinstance(item, Atom),      'Invalid arguments: list is not a list of iprPy.Atoms'
                self.__atoms = arg1
        
        #Access per-atom values if first argument is an integer
        elif isinstance(arg1, int):
            assert arg1 >= 0 and arg1 < self.natoms(),  'Invalid arguments: atom index out of range' 
            a_id = arg1
        
            #Return a copy of the atom if no other arguments supplied
            if arg2 is None:
                assert arg3 is None,               'Invalid arguments: third argument has value, second does not'
                if scale:
                    return self.scale(self.__atoms[a_id])
                else:
                    return deepcopy(self.__atoms[a_id])
            
            #Set the atom to arg2 if it is an Atom
            elif isinstance(arg2, Atom):
                assert arg3 is None,                'Invalid arguments: third argument has no meaning here'
                self.__atoms[a_id] = arg2
            
            #Set or return a per-atom property
            elif isinstance(arg2, (str, unicode)):
                
                #Return a per-atom property
                if arg3 is None:
                    if arg2 == 'pos' and scale:
                        return self.scale(self.__atoms[a_id].pos())
                    else:
                        return self.__atoms[a_id].prop(arg2)
                
                #Set a per-atom property
                else:
                    if arg2 == 'pos' and scale:
                        val = self.__atoms[a_id].pos(self.unscale(arg3))
                    else:
                        val = self.__atoms[a_id].prop(arg2, arg3)
                    if val is not None:
                        return val
            
            else:
                raise TypeError('Invalid argument types')
        else:
            raise TypeError('Invalid argument types')
    
    def box(self, arg1=None):
        #Get properties of the system's box
        if arg1 is None:
            return self.__box
        else:
            return self.__box.get(arg1)
    
    def pbc(self, arg1=None, arg2=None, arg3=None):
        #Get or set periodic boundary conditions
        if arg1 is None:
            assert arg2 is None,   'Terms should be set in order'
            return self.__pbc
        elif isinstance(arg1, (list, tuple, np.ndarray)) and len(arg1) == 3:
            assert isinstance(arg1[0], bool) and isinstance(arg1[1], bool) and isinstance(arg1[2], bool), 'pbcs must be True/False'
            assert arg2 is None and arg3 is None,   'Invalid pbc arguments'
            self.__pbc = tuple(arg1)
        elif isinstance(arg1, int) and arg1 >= 0 and arg1 < 3:
            assert arg3 is None,   'Invalid pbc arguments'
            if arg2 is None:
                return self.__pbc[arg1]
            else:
                assert isinstance(arg2, bool),     'pbcs must be True/False'
                newpbc = list(self.__pbc)
                newpbc[arg1] = arg2
                self.__pbc = tuple(newpbc)
        elif isinstance(arg1, bool) and isinstance(arg2, bool) and isinstance(arg3, bool):
            self.__pbc = (arg1, arg2, arg3)
        else:
            raise TypeError('Invalid pbc arguments')
    
    def prop(self, term, arg1=None, arg2=None, arg3=None, scale=None):
        assert isinstance(term, (str, unicode)), 'property term needs to be a string'
        
        #Deal with atoms properties
        if term == 'atoms':
            if scale is None:
                scale = False
            output = self.atoms(arg1=arg1, arg2=arg2, arg3=arg3, scale=scale)
            if output is not None:
                return output

        #Deal with box properties
        elif term == 'box':
            assert arg2 is None and arg3 is None,   'Only one argument supported for box'
            assert scale is None,                   'scale argument is only for atoms'
            output = self.box(arg1=arg1)
            if output is not None:
                return output        
        
        #Deal with pbc properties
        elif term == 'pbc':
            assert scale is None,                   'scale argument is only for atoms'
            output = self.pbc(arg1=arg1, arg2=arg2, arg3=arg3)
            if output is not None:
                return output 
        
        #Deal with custom properties
        else:
            assert arg2 is None and arg3 is None,   'Only one argument supported for custom properties'
            assert scale is None,                   'scale argument is only for atoms'
            
            if arg1 is None:
                try:
                    return self.__prop[term]
                except:
                    return None
            else:
                self.__prop[term] = arg1
                
            
    
    
    def scale(self, point):
        #Converts an atom or 3D vector position from absolute to reduced-box coordinates
        if isinstance(point, Atom):
            pos = point.pos() - self.box('origin')
        elif isinstance(point, (list, tuple, np.ndarray)) and len(point) == 3:
            pos = point - self.box('origin')
        else:
            raise TypeError('scale only works on atoms or 3D vectors')
        
        avect = self.box('avect')
        bvect = self.box('bvect')
        cvect = self.box('cvect')
        spos = np.zeros(3)
        
        spos[2] = pos[2] / cvect[2]
        pos -= spos[2] * cvect
        spos[1] = pos[1] / bvect[1]
        pos -= spos[1] * bvect
        spos[0] = pos[0] / avect[0]
        pos -= spos[0] * avect
            
        assert np.allclose(pos, np.zeros(3)), 'error!'
        
        if isinstance(point, Atom):
            return Atom(point.atype(), spos)
        else:
            return spos
          
    def unscale(self, point):
        #Converts an atom or 3D vector position from reduced-box to absolute coordinates
        if isinstance(point, Atom):
            spos = point.pos()
        elif isinstance(point, (list, tuple, np.ndarray)) and len(point) == 3:
            spos = point
        else:
            raise TypeError('unscale only works on atoms or 3D vectors')
            
        avect = self.box('avect')
        bvect = self.box('bvect')
        cvect = self.box('cvect')
        pos = spos[0] * avect + spos[1] * bvect + spos[2] * cvect + self.box('origin')
        
        if isinstance(point, Atom):
            return Atom(point.atype(), pos)
        else:
            return pos
    
    def natoms(self):
        #Return the number of atoms in the system
        return len(self.__atoms)
    
    def natypes(self):
        #Return the max atype value in all of the atoms
        nt = 0
        for atom in self.__atoms:
            if atom.atype() > nt:
                nt = atom.atype()
        return nt
    
    def dvect(self, a1, a2):
        #compute shortest distance between two atoms taking pbc information into account
        
        if isinstance(a1, int):
            pos1 = self.atoms(a1, 'pos')
        elif isinstance(a1, np.ndarray) and len(a1) == 3:
            pos1 = a1
        elif isinstance(a1, Atom):
            pos1 = a1.pos()
        else:
            raise TypeError('unsupported type for dvect')
        
        if isinstance(a2, int):
            pos2 = self.atoms(a2, 'pos')
        elif isinstance(a2, np.ndarray) and len(a2) == 3:
            pos2 = a2
        elif isinstance(a2, Atom):
            pos2 = a2.pos()
        else:
            raise TypeError('unsupported type for dvect')
    
        if self.pbc(0):
            xcheck = xrange(-1, 2)
        else:
            xcheck = xrange(1)
        if self.pbc(1):
            ycheck = xrange(-1, 2)
        else:
            ycheck = xrange(1)
        if self.pbc(2):
            zcheck = xrange(-1, 2)
        else:
            zcheck = xrange(1)            
        
        delta = pos2 - pos1
        
        for x in xcheck:
            for y in ycheck:
                for z in zcheck:
                    test = delta + x * self.box('avect') + y * self.box('bvect') + z * self.box('cvect')
                    if mag(test) < mag(delta):
                        delta = test
                        
        return delta
    
    def wrap(self):
        #Wrap atoms around periodic boundaries
        for i in xrange(self.natoms()):
            spos = self.scale(self.atoms(i, 'pos'))
            if spos[0] < 0 or spos[0] > 1 or spos[1] < 0 or spos[1] > 1 or spos[2] < 0 or spos[2] > 1:
                for j in xrange(3):
                    if self.pbc(j):
                        while spos[j] < 0:
                            spos[j] += 1
                        while spos[j] >= 1:
                            spos[j] -= 1
                self.atoms( i, 'pos', self.unscale(spos) )        
    
    def pt_defect(self, ptdtype='v', atype=None, pos=None, ptd_id=None, db_vect=None, shift=False):
        #Returns two new systems, one with and one without a point defect with matching atom ids.  Defect is given largest id value
        
        #Check that ptdtype and shift are valid
        assert ptdtype == 'v' or ptdtype == 'i' or ptdtype == 's' or ptdtype == 'db',       'Invalid ptdtype. Options are: v, i, s, or db'
        assert isinstance(shift, bool),                                                     'shift must be a bool'
        
        natoms = self.natoms()
        
        #Validate vacancy inputs
        if ptdtype == 'v':
            assert atype is None,                                                           'atype is meaningless for vacancy insertion'
            assert db_vect is None,                                                         'db_vect is meaningless for vacancy insertion'
            assert pos is not None or ptd_id is not None,                                   'pos or ptd_id are needed for vacancy insertion'
            if pos is not None:
                assert ptd_id is None,                                                      'pos and ptd_id cannot both be supplied!'
                assert isinstance(pos, (list, tuple, np.ndarray)) and len(pos) == 3,        'pos must be a 3D vector position'
            else:
                assert isinstance(ptd_id, int) and ptd_id >= 0 and ptd_id < natoms,         'ptd_id must be an integer between 0 and natoms of the system'
            
        #Validate interstitial inputs
        elif ptdtype == 'i':
            assert isinstance(atype, int) and atype > 0,                                    'atype required for interstitial insertion and must be a positive integer'
            assert db_vect is None,                                                         'db_vect is meaningless for interstitial insertion'
            assert isinstance(pos, (list, tuple, np.ndarray)) and len(pos) == 3,            'pos required for interstitial insertion and must be a 3D vector position'
            assert ptd_id is None,                                                          'ptd_id is meaningless for interstitial insertion'
                    
        #Validate substitutional inputs
        elif ptdtype == 's':
            assert isinstance(atype, int) and atype > 0,                                    'atype required for substitutional insertion and must be a positive integer'
            assert db_vect is None,                                                         'db_vect is meaningless for substitutional insertion'
            assert pos is not None or ptd_id is not None,                                   'pos or ptd_id are needed for substitutional insertion'
            if pos is not None:
                assert ptd_id is None,                                                      'pos and ptd_id cannot both be supplied!'
                assert isinstance(pos, (list, tuple, np.ndarray)) and len(pos) == 3,        'pos must be a 3D vector position'
            else:
                assert isinstance(ptd_id, int) and ptd_id >= 0 and ptd_id < natoms,         'ptd_id must be an integer between 0 and natoms of the system'
        
        #Validate dumbbell inputs
        elif ptdtype == 'db':
            assert isinstance(atype, int) and atype > 0,                                    'atype required for dumbbell insertion and must be a positive integer'
            assert isinstance(db_vect, (list, tuple, np.ndarray)) and len(pos) == 3,        'db_vect required for dumbbell insertion and must be a 3D vector position'
            assert pos is not None or ptd_id is not None,                                   'pos or ptd_id are needed for dumbbell insertion'
            if pos is not None:
                assert ptd_id is None,                                                      'pos and ptd_id cannot both be supplied!'
                assert isinstance(pos, (list, tuple, np.ndarray)) and len(pos) == 3,        'pos must be a 3D vector position'
            else:
                assert isinstance(ptd_id, int) and ptd_id >= 0 and ptd_id < natoms,         'ptd_id must be an integer between 0 and natoms of the system'
        
        #check for atoms at pos if supplied
        if pos is not None:
            pos = np.array(pos)
            ptd_id = None
            for i in xrange(natoms):
                if np.allclose( self.atoms(i,'pos'), pos ):
                    ptd_id = i
                    break
            
            #Interstitial should not have an atom at pos, all others should
            if ptdtype == 'i':
                assert ptd_id is None,                                                      'Atom already at pos!'
            else:
                assert ptd_id is not None,                                                  'No atom found at pos!'
        
        #Set pos if ptd_id is supplied            
        else:
            pos = self.atoms(ptd_id, 'pos')
        
        #Validate substitutional atype is different than current atype
        if ptdtype == 's':
            assert atype != self.atoms(ptd_id, 'atype'),                                    'Identified atom already is of atype!'
        
        #Set shift
        if shift:
            cshift = -pos
        else:
            cshift = np.zeros(3)
            
        #Create new lists of atoms associated with the perfect and defect systems
        patoms = []
        datoms = []
            
        #Copy over all non-defect atoms shifting atom ids (and positions)
        j = 0
        for i in xrange(natoms):
            if i != ptd_id:
                patoms.append( self.atoms(i) + cshift )
                datoms.append( self.atoms(i) + cshift )
                j += 1
        
        #if vacancy, only add atom at pos + cshift to perfect system
        if ptdtype =='v':
            assert j == natoms-1,                                                           'Error copying atoms!'
            patoms.append( self.atoms(ptd_id) + cshift )
        
        #if interstitial, add atom at position pos + cshift
        elif ptdtype =='i':
            assert j == natoms,                                                             'Error copying atoms!'
            datoms.append( Atom( atype, pos + cshift ) )
                
        #if substitution, set defect atom type to atype
        elif ptdtype =='s':
            assert j == natoms-1,                                                           'Error copying atoms!'
            datoms.append( Atom( atype, pos + cshift ) )
            patoms.append( self.atoms(ptd_id) + cshift )
                
        #if dumbbell, add atoms at pos + shift +- d 
        elif ptdtype =='db':
            assert j == natoms-1,                                                           'Error copying atoms!'
            datoms.append( self.atoms(ptd_id) + cshift - d ) 
            datoms.append( Atom( atype, pos + cshift + d ) )
            patoms.append( self.atoms(ptd_id) + cshift )
                
        psys = System(atoms=patoms, box=deepcopy(self.box()), pbc=self.pbc())
        dsys = System(atoms=datoms, box=deepcopy(self.box()), pbc=self.pbc())
        
        #if shift, shift box position and wrap atoms around periodic boundaries
        if shift:
            psys.box().set_origin(self.box('origin') + cshift)
            dsys.box().set_origin(self.box('origin') + cshift)

            zzz = psys.scale(np.array([0.0, 0.0, 0.0]))

            cshift2 = np.zeros(3)
            for i in xrange(3):
                if psys.pbc(i):
                    cshift2[i] = 0.5 - zzz[i]
            cshift2 = cshift2[0]*self.box('avect') + cshift2[1]*self.box('bvect') + cshift2[2]*self.box('cvect')
            
            psys.box().set_origin(psys.box('origin') - cshift2)
            dsys.box().set_origin(dsys.box('origin') - cshift2)
            psys.wrap()
            dsys.wrap()
        
        return psys, dsys
        
    def neighbors(self, cutoff, cmult=2):
        #Build neighbor list for all atoms using cutoff.  cmult alters how many bins are created, with cmult=2 often the fastest
        natoms = self.natoms()
        vects = [self.box('avect'), self.box('bvect'), self.box('cvect')]
               
        def box_iter(num):
            #Iterates over unique x,y,z combinations where each x,y,z can equal +-num.
            #Excludes 0,0,0 and equal but opposite combinations (i.e. x,y,z used, -x,-y,-z excluded)
            z = -num
            end = False
            while z <= 0:
                y = -num
                while y <= num:
                    x = -num
                    while x <= num:
                        if x ==0 and y==0 and z==0:
                            end=True
                            break
                        yield x,y,z
                        x+=1
                    if end:
                        break
                    y+=1
                if end:
                    break
                z+=1
        
        #Determine orthogonal superbox that fully encompases the system box 
        lo_corner = self.box('origin')
        hi_corner = self.box('origin')
        for x in xrange(2):
            for y in xrange(2):
                for z in xrange(2):
                    corner = self.box('origin') + x * vects[0] + y * vects[1] + z * vects[2]
                    for i in xrange(3):
                        if corner[i] - cutoff < lo_corner[i]:
                            lo_corner[i] = corner[i] - cutoff
                        if corner[i] +  cutoff > hi_corner[i]:
                            hi_corner[i] = corner[i] + cutoff
        
        #Create bins
        numbins = np.zeros(3, dtype=int)
        binsize = (cutoff / cmult)
        for i in xrange(3):
            numbins[i] = int((hi_corner[i] - lo_corner[i]) / binsize) + 1
            hi_corner[i] = lo_corner[i] + numbins[i] * binsize
        bins = [[[[] for z in xrange(numbins[2])] for y in xrange(numbins[1])] for x in xrange(numbins[0])]
        real = [[[False for z in xrange(numbins[2])] for y in xrange(numbins[1])] for x in xrange(numbins[0])]
        
        #Fill superbox with atoms 
        for i in xrange(natoms):
            #Include copies along periodic directions
            check = [[0],[0],[0]]
            for p in xrange(3):
                if self.pbc(p):
                    check[p] = xrange(-1,2)
            
            #Add atoms to bins
            for x in check[0]:
                for y in check[1]:
                    for z in check[2]:
                        pos = self.atoms(i, 'pos') + x * vects[0] + y * vects[1] + z * vects[2] - lo_corner         
                        xb = int(pos[0] / binsize)
                        yb = int(pos[1] / binsize)
                        zb = int(pos[2] / binsize)
                        if xb >= 0 and xb < numbins[0] and yb >= 0 and yb < numbins[1] and zb >= 0 and zb < numbins[2]:
                            bins[xb][yb][zb].append(i)
                            if x == 0 and y == 0 and z == 0:
                                real[xb][yb][zb] = True

        #Go through bins and build neighbor list
        nlist = [[] for i in xrange(natoms)] 
        for z in xrange(numbins[2]):
            for y in xrange(numbins[1]):
                for x in xrange(numbins[0]):
                    
                    #If the bin contains any real (not copy) atoms
                    if real[x][y][z]:
                        #For atom u in bin
                        for u in xrange(len(bins[x][y][z])):
                            id_u = bins[x][y][z][u]
                            #for atom v in same bin
                            for v in xrange(u):
                                id_v = bins[x][y][z][v]
                                #Compare distance between u and v
                                if mag(self.dvect(id_u, id_v)) < cutoff:
                                    #Add neighbors to each other if not already paired
                                    if id_v not in nlist[id_u] and id_u != id_v:
                                        nlist[id_u].append(id_v)
                                        nlist[id_v].append(id_u)
                                      
                            #iterate over neighbor bins and compare to cutoff
                            for dx, dy, dz in box_iter(cmult):
                                #iterate over all atoms w in neighboring bin
                                for w in xrange(len(bins[x+dx][y+dy][z+dz])):
                                    id_w = bins[x+dx][y+dy][z+dz][w]
                                    if mag(self.dvect(id_u, id_w)) < cutoff:
                                        #Add neighbors to each other if not already paired
                                        if id_w not in nlist[id_u] and id_u != id_w:
                                            nlist[id_u].append(id_w)
                                            nlist[id_w].append(id_u)
    
        for i in xrange(natoms):
            self.atoms(i, 'coordination', len(nlist[i]))
        
        self.prop('nlist', nlist)

    def write_nlist(self, fname):
        nlist = self.prop('nlist')
        
        if nlist is None:
            raise ValueError('nlist not defined for this system!')
        else:
            with open(fname, 'w') as f:
                f.write('#Generated neighbor list\n')
                f.write('#index n_index_1 n_index_2 ...\n')
                for i in xrange(len(nlist)):
                    f.write(str(i))
                    for n in nlist[i]:
                        f.write(' ' + str(n))
                    f.write('\n')
    
    def read_nlist(self, fname):
        nlist = [[] for i in xrange(self.natoms())]
        
        with open(fname, 'r') as f:
            for line in f:
                if len(line) > 0:
                    terms = line.split()
                    if terms[0][0] != '#':
                        i = int(terms[0])
                        self.atoms(i, 'coordination', len(terms[1:]))
                        for j in terms[1:]:
                            nlist[i].append(j)
        
        self.prop('nlist', nlist)
                        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        