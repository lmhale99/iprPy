import numpy as np
from collections import OrderedDict

class Atom:
    #initialize Atom instance
    def __init__(self, type=0, pos=np.zeros(3)):
        self.__set_type(type)
        self.__set_pos(pos)
        self.__prop = OrderedDict()
    
    #Print atom type and coordinates when converted to a string
    def __str__(self):
        return '%i %.13e %.13e %.13e'%(self.__type, self.__pos[0], self.__pos[1], self.__pos[2]) 
    def __add__(self, y):    
         return Atom(self.__type, self.__pos + y)
    def __sub__(self, y):    
         return Atom(self.__type, self.__pos - y)
    def __mul__(self, y):
         return Atom(self.__type, self.__pos * y) 
    def __rmul__(self, y):
         return Atom(self.__type, y * self.__pos)
    
    
    #Set per-atom property value according to property name 
    def set(self, name, value):
        if name == 'type':
            self.__set_type(value)
        elif name == 'pos':
            self.__set_pos(value)
        elif name == 'x' or name == 'xu':
            self.__pos[0] = float(value)
        elif name == 'y' or name == 'yu':
            self.__pos[1] = float(value)
        elif name == 'z' or name == 'zu':
            self.__pos[2] = float(value)     
        else:
            self.__prop[name] = value
    
    #Get per-atom property value using property name    
    def get(self, name):
        if name == 'type':
            return self.__type
        elif name == 'pos':
            return self.__pos
        elif name == 'x' or name == 'xu':
            return self.__pos[0]
        elif name == 'y' or name == 'yu':
            return self.__pos[1]
        elif name == 'z' or name == 'zu':
            return self.__pos[2]
        else:
            try:
                return self.__prop[name]
            except:
                return None
    
    #Set atom type and check that it is an integer
    def __set_type(self, type):
        if isinstance(type, float):
            if np.isclose(type % 1, 0.0):
                self.__type = int(round(type))
            else:
                raise ValueError('invalid float for converting atom type value to int')
        else:
            self.__type = int(type)
    
    #Set atom coordinates if supplied value is list, tuple, or numpy array of length 3
    def __set_pos(self, pos):
        if len(pos) != 3:
            raise ValueError('supplied position coordinates do not have three dimensions')
        
        if isinstance( pos, (list, tuple) ):
            self.__pos = np.empty(3)
            for i in xrange(3):
                self.__pos[i] = float(pos[i])
        elif isinstance(pos, np.ndarray):
            self.__pos = pos
        else:
            raise ValueError('supplied position coordinates in unsupported format')       
    
    #Return list of assigned per-atom properties            
    def list(self):
        l = ['type','x','y','z']
        for k,v in self.__prop.iteritems():
            l.append(k)
        return l