from collections import OrderedDict
import numpy as np
from copy import deepcopy

from Atom import Atom
from AtomType import AtomType
     
class System:
    def __init__(self, atoms=[], box=np.zeros((3,3)), pbc=(False,False,False), atomtypes=[]):
        self.atoms = atoms
        self.box = box
        self.pbc = pbc
        self.atomtypes = atomtypes
        self.__prop = {}
    
    def get(self, name):
        if name == 'atoms':
            return self.atoms
        elif name == 'box':
            return self.box
        elif name == 'pbc':
            return self.pbc
        elif name == 'atomtypes':
            return self.atomtypes
        else:
            try:
                return self.__prop[name]
            except:
                return None
                
    def set(self, name, value):
        if name == 'atoms':
            self.atoms = value
        elif name == 'box':
            self.box = value
        elif name == 'pbc':
            self.pbc = value
        elif name == 'atomtypes':
            self.atomtypes = value
        elif name == 'cij':
            self.set_cij(cij)
        else:
            self.__prop[name] = value
    
    def natoms(self):
        return len(self.atoms)
    
    #ntypes returns the max atype value in atoms
    def ntypes(self):
        nt = 0
        for atom in self.atoms:
            if atom.get('type') > nt:
                nt = atom.get('type')
        return nt
    
    #compute shortest distance between two atoms taking pbc information into account
    def dvect(self, a1, a2):
        if isinstance(a1,int):
            pos1 = self.atoms[a1].get('pos')
        elif isinstance(a1, np.ndarray) and len(a1) == 3:
            pos1 = a1
        elif isinstance(a1, Atom):
            pos1 = a1.get('pos')
        else:
            raise TypeError('unsupported type for dvect')
        
        if isinstance(a2,int):
            pos2 = self.atoms[a2].get('pos')
        elif isinstance(a2, np.ndarray) and len(a2) == 3:
            pos2 = a2
        elif isinstance(a2, Atom):
            pos2 = a2.get('pos')
        else:
            raise TypeError('unsupported type for dvect')
    
        delta = pos2 - pos1
        for i in range(0,3):
            if self.pbc[i] == True:
                if delta[i] > (self.box[i,1] - self.box[i,0]) / 2:
                    delta[i] = delta[i] - (self.box[i,1] - self.box[i,0])
                elif delta[i] < -(self.box[i,1] - self.box[i,0]) / 2:
                    delta[i] = delta[i] + (self.box[i,1] - self.box[i,0])
        return delta
        
    #Insert a point defect (ptdtype ='v','i','db','s') at coordinates pos or atom id ptd_id.
    #For ptdtype = 'db', dumbbell interstitial will be created using dumbbell vector d.
    def pt_defect(self, ptdtype='v', atype=1, pos=np.array([0.,0.,0.]), ptd_id=0, d=np.array([0.,0.,0.]), shift = False):
        natoms = len(self.atoms)
        
        #initial checks
        #Make sure dumbbell vector is supplied for dumbbell
        if ptdtype == 'db' and np.allclose(d, np.zeros(3)):
            raise ValueError('Dumbbell vector not specified!')
            
        #check id defect identification
        if ptd_id > 0 and ptdtype != 'i':
            if np.allclose(pos, np.zeros(3)):
                if ptd_id <= natoms:
                    pos_id = ptd_id
                    pos = self.atoms[pos_id-1].get('pos')
                else:
                    raise ValueError('Atom id '+str(ptd_id)+' greater than number of atoms '+str(natoms)+'!')
            else:
                raise ValueError('Id and coordinates both supplied for defect creation!')
                
        #check for atoms at pos
        else:
            pos_id = 0
            for i in xrange(natoms):
                if np.allclose(self.atoms[i].get('pos'), pos):
                    pos_id = i+1
                    break
            #if vacancy, dumbbell or substitutional, then an atom should be at pos
            if (ptdtype=='v' or ptdtype=='db' or ptdtype=='s') and pos_id == 0:
                raise ValueError('No atom found at '+str(pos)+'!')
                
            #if interstitial, then no atom should be at pos
            elif ptdtype=='i' and pos_id > 0:
                raise ValueError('Atom '+str(pos_id)+' already at '+str(pos)+'!')

            #if substitutional, atom at pos should not already be of atom type atype
            elif ptdtype == 's' and pos_id > 0 and atype == self.atoms[pos_id-1].get('type'):
                raise ValueError('Atom at '+str(pos)+' already of atom type '+str(atype)+'!')
        
        #set pos shift if shift == True
        cshift = np.zeros(3)
        if shift:
            cshift = -pos
        
        
        #Make copy systems. dsys will contain defect, while psys will not but have atom id's consistent with dsys
        psys = deepcopy(self)
        psys.atoms = []
        dsys = deepcopy(self)
        dsys.atoms = []
            
        #Copy over all non-defect atoms shifting atom ids (and positions)
        j = 0
        for i in xrange(natoms):
            if i != pos_id-1:
                newposition = self.atoms[i].get('pos') + cshift
                for k in xrange(3):
                    while newposition[k] < self.box[k,0]:
                        newposition[k] += (self.box[k,1] - self.box[k,0])
                    while newposition[k] > self.box[k,1]:
                        newposition[k] -= (self.box[k,1] - self.box[k,0])
                psys.atoms.append(Atom(self.atoms[i].get('type'), newposition))
                dsys.atoms.append(Atom(self.atoms[i].get('type'), newposition))
                j += 1
        
        #if interstitial, add atom at position pos + cshift
        if ptdtype =='i':
            if j == natoms:
                dsys.atoms.append(Atom(atype, pos + cshift))
            else:
                raise ValueError('Error copying atoms!')
                
        #if substitution, set defect atom type to atype
        elif ptdtype =='s':
            if j == natoms-1:
                dsys.atoms.append(Atom(atype,                            pos + cshift))
                psys.atoms.append(Atom(self.atoms[pos_id-1].get('type'), pos + cshift))
            else:
                raise ValueError('Error copying atoms!')
                
        #if dumbbell, add atoms at pos + shift +- d 
        elif ptdtype =='db':
            if j == natoms-1:
                dsys.atoms.append(Atom(self.atoms[pos_id-1].get('type'), pos + cshift - d))
                dsys.atoms.append(Atom(atype,                            pos + cshift + d))
                psys.atoms.append(Atom(self.atoms[pos_id-1].get('type'), pos + cshift))
            else:
                raise ValueError('Error copying atoms!')
                
        #if vacancy, don't add defect atom to dsys
        elif ptdtype =='v':
            if j == natoms-1:
                psys.atoms.append(Atom(self.atoms[pos_id-1].get('type'), pos + cshift))
            else:    
                raise ValueError('Error copying atoms!')
            
        return psys, dsys
        
    #Use binning to find all neighbors within the cutoff distance for all atoms
    #cmult alters how many boxes are created, with cmult=2 often the fastest for most cases
    def neighbors(self, cutoff, cmult=2):
        natoms = self.natoms()
        box = self.box
        atoms = self.atoms
        pbc = self.pbc
        nlist = [[0] for y in xrange(natoms)]
        
        #Iterates over unique x,y,z combinations where each x,y,z can equal +-num.
        #Does not include 0,0,0 or identical but opposite combinations
        #i.e. if x,y,z is given, then -x,-y,-z is excluded.
        def box_iter(num):
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
        
        #For each direction, binsize will be at least cutoff/cmult
        #If periodic, bins will evenly divide system dimension
        #If not periodic, bin dimension will be cutoff/cmult
        if pbc[0]:
            xbins = int((box[0,1] - box[0,0]) / (cutoff / cmult)) + 2 * cmult
            xbinsize = (box[0,1] - box[0,0]) / (xbins - 2 * cmult)
        else:
            xbinsize = cutoff / cmult
            xbins = int((box[0,1] - box[0,0]) / xbinsize) + 2 * cmult + 1
        if pbc[1]:
            ybins = int((box[1,1] - box[1,0]) / (cutoff / cmult)) + 2 * cmult
            ybinsize = (box[1,1] - box[1,0]) / (ybins - 2 * cmult)
        else:
            ybinsize = cutoff / cmult
            ybins = int((box[1,1] - box[1,0]) / ybinsize) + 2 * cmult + 1
        if pbc[2]:
            zbins = int((box[2,1] - box[2,0]) / (cutoff / cmult)) + 2 * cmult
            zbinsize = (box[2,1] - box[2,0]) / (zbins - 2 * cmult)
        else:
            zbinsize = cutoff / cmult
            zbins = int((box[2,1] - box[2,0]) / zbinsize) + 2 * cmult + 1

        bins = [[[[0] for z in xrange(zbins)] for y in xrange(ybins)] for x in xrange(xbins)]
        
        #grow the real bins by assigning atoms into them
        for i in xrange(natoms):
            #Wrap atoms around periodic directions if necessary
            pos = atoms[i].get('pos')
            for p in xrange(3):
                if pbc[p]:
                    while pos[p] < box[p,0]:
                        pos[p] += (box[p,1] - box[p,0])
                    while pos[p] > box[p,1]:
                        pos[p] -= (box[p,1] - box[p,0])
                        
            xb = int((pos[0] - box[0,0]) / xbinsize) + cmult
            yb = int((pos[1] - box[1,0]) / ybinsize) + cmult
            zb = int((pos[2] - box[2,0]) / zbinsize) + cmult
     
            if bins[xb][yb][zb][0] == 0:  
                bins[xb][yb][zb][0] = i + 1
            else:
                bins[xb][yb][zb].append(i + 1)
            
        #handle periodicity by copying atoms to the imaginary bins 
        if pbc[0]:
            for y in xrange(ybins):
                for z in xrange(zbins):
                    for c in xrange(cmult):
                        bins[c][y][z] = bins[-2*cmult+c][y][z]
                        bins[-cmult+c][y][z] = bins[cmult+c][y][z]

        if pbc[1]:
            for x in xrange(xbins):
                for z in xrange(zbins):
                    for c in xrange(cmult):
                        bins[x][c][z] = bins[x][-2*cmult+c][z]
                        bins[x][-cmult+c][z] = bins[x][cmult+c][z]
        
        if pbc[2]:
            for x in xrange(xbins):
                for y in xrange(ybins):
                    for c in xrange(cmult):
                        bins[x][y][c] = bins[x][y][-2*cmult+c]
                        bins[x][y][-cmult+c] = bins[x][y][cmult+c]
       
        #cycle through the real bins 
        for z in xrange(cmult, zbins - cmult):
            for y in xrange(cmult, ybins - cmult):
                for x in xrange(cmult, xbins - cmult):
                    
                    #If there are atoms in the bin
                    if bins[x][y][z][0] > 0:
                        #Iterate over all atoms in a bin
                        for u in xrange(len(bins[x][y][z])):
                            id_u = bins[x][y][z][u]
                            #Compare to all other atoms in the same bin
                            for v in xrange(u):
                                id_v = bins[x][y][z][v]
                                if mag(self.dvect(id_u-1, id_v-1)) < cutoff:
                                    #Add neighbors to each other if not already paired
                                    new = True
                                    for ch in xrange(nlist[id_u-1][0]):
                                        if nlist[id_u-1][ch+1] == id_v: 
                                            new = False
                                    if new:
                                        nlist[id_u-1][0] += 1
                                        nlist[id_u-1].append(id_v)
                                        nlist[id_v-1][0] += 1
                                        nlist[id_v-1].append(id_u)
                                                                    
                            #iterate over neighbor bins and compare to cutoff
                            for dx, dy, dz in box_iter(cmult):
                                #If there are atoms in the bin
                                if bins[x+dx][y+dy][z+dz][0] > 0:
                                    #iterate over all atoms w in neighboring bin
                                    for w in xrange(len(bins[x+dx][y+dy][z+dz])):
                                        id_w = bins[x+dx][y+dy][z+dz][w]
                                        if mag(self.dvect(id_u-1, id_w-1)) < cutoff:
                                            #Add neighbors to each other if not already paired
                                            new = True
                                            for ch in xrange(nlist[id_u-1][0]):
                                                if nlist[id_u-1][ch+1] == id_w: 
                                                    new = False
                                            if new:
                                                nlist[id_u-1][0] += 1
                                                nlist[id_u-1].append(id_w)
                                                nlist[id_w-1][0] += 1
                                                nlist[id_w-1].append(id_u)
        
        for i in xrange(natoms):
            self.atoms[i].set('coordination', nlist[i][0])
        
        self.set('nlist', nlist)
    
    def elements(self):
        elist = []
        for at in self.atomtypes:
            elist.append(at.get('element'))
        return elist
        
    def masses(self):
        mlist = []
        for at in self.atomtypes:
            mlist.append(at.get('mass'))
        return mlist    
                  
def mag(vect):
    m = 0
    for v in vect:
        m += v**2
    return (m)**.5
