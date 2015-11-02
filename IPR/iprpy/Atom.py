import numpy as np
from collections import OrderedDict
from copy import deepcopy
import numpy as np

class Atom:
    def __init__(self, atype=0, pos=np.zeros(3)):
        #initialize Atom instance
        self.atype(atype)
        self.pos(pos)
        self.__prop = OrderedDict()
    
    def __str__(self):
        #Print atom type and coordinates when converted to a string
        return '%i %.13e %.13e %.13e'%(self.__atype, self.__pos[0], self.__pos[1], self.__pos[2]) 
    def __add__(self, y):    
        newatom = deepcopy(self)
        newatom.pos(self.__pos + y)
        return newatom
    def __sub__(self, y):    
        newatom = deepcopy(self)
        newatom.pos(self.__pos - y)
        return newatom
    def __mul__(self, y):
        newatom = deepcopy(self)
        newatom.pos(self.__pos * y)
        return newatom
    def __rmul__(self, y):
        newatom = deepcopy(self)
        newatom.pos(y * self.__pos)
        return newatom
         
    def atype(self, atype=None):
        #Get or set the atom's type
        if atype is None:
            #Return atom type
            return self.__atype
        else:
            #Set atom type if integer
            assert isinstance(atype, int),  'Atom type must be an integer'
            self.__atype = atype    
    
    def pos(self, arg1=None):
        #Get or set the atom's position
        if arg1 is None:
            #Return atom position
            return deepcopy(self.__pos)
        elif isinstance(arg1, int) and arg1 >=0 and arg1 < 3:
            return self.__pos[arg1]
        elif isinstance(arg1, (list, tuple, np.ndarray)) and len(arg1) == 3:
            self.__pos = np.array(arg1, dtype=np.float)
        else:
            raise TypeError('Invalid argument')
    
    def prop(self, term, value=None):
        #Get or set per-atom properties
        assert isinstance(term, (str, unicode)), 'property term needs to be a string'
        if value is None:
            if term == 'atype':
                return self.atype()
            elif term == 'pos':
                return self.pos()
            else:
                try:
                    return self.__prop[term]
                except:
                    return None
        else:
            if term == 'atype':
                self.atype(value)
            elif term == 'pos':
                val = self.pos(value)
                if val is not None:
                    return val
            else:
                self.__prop[term] = value
        
    def prop_list(self):
        #Returns list of assigned per-atom properties
        l = ['atype', 'pos']
        for k, v in self.__prop.iteritems():
            l.append(k)
        return l