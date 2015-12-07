import numpy as np
from collections import OrderedDict
from copy import deepcopy

class Atom:
    def __init__(self, atype=0, pos=np.zeros(3), init_size=30):
        #initialize Atom instance
        assert isinstance(init_size, int) and init_size >= 4, 'Invalid init_size term'
        self.__values = np.empty(init_size)
        self.__prop_names = ['atype', 'pos']
        self.__prop_dtype = [int,     float]
        self.__prop_shape = [(),      (3L,)]

        self.atype(atype)
        self.pos(pos)
    
    def __str__(self):
        #Print atom type and coordinates when converted to a string
        return '%i %.13e %.13e %.13e'%(self.atype(), self.pos(0), self.pos(1), self.pos(2)) 
    def __add__(self, y):    
        newatom = deepcopy(self)
        newatom.pos(self.pos() + y)
        return newatom
    def __sub__(self, y):    
        newatom = deepcopy(self)
        newatom.pos(self.pos() - y)
        return newatom
    def __mul__(self, y):
        newatom = deepcopy(self)
        newatom.pos(self.pos() * y)
        return newatom
    def __rmul__(self, y):
        newatom = deepcopy(self)
        newatom.pos(y * self.pos())
        return newatom
    
    def prop(self, term, arg1=None, arg2=None):
        #Get or set per-atom properties
        assert isinstance(term, (str, unicode)), 'property term needs to be a string'
        
        #Return full term if no arguments supplied
        if arg1 is None and arg2 is None:
            
            #Test if term has been assigned
            try:
                p_index = self.__prop_names.index(term)
            except:
                return None
            
            start = self.__allsum(self.__prop_shape[:p_index])
            shape = self.__prop_shape[p_index]
            dtype = self.__prop_dtype[p_index]
            
            #Handle scalars
            if len(shape) == 0:
                return np.array(self.__values[start], dtype=dtype)
            
            #Handle vectors
            elif len(shape) == 1:
                end = start + shape[0]
                return np.array(self.__values[start:end], dtype=dtype)
            
            #Handle 2D arrays
            elif len(shape) == 2:
                property = np.empty(shape, dtype=dtype)
                for i in xrange(shape[0]):
                    for j in xrange(shape[1]):
                        property[i,j] = self.__values[start + i * shape[0] + j]
                return property
        
        #if an argument is supplied
        else:
            arg1 = np.array(arg1)
            
            #Append term, dtype info, and shape info if new property
            if term not in self.prop_list():
                assert len(arg1.shape) <= 2, 'Terms must be scalars, 1D vectors or 2D arrays'
                self.__prop_names.append(term)
                self.__prop_dtype.append(arg1.dtype)
                self.__prop_shape.append(arg1.shape)
                
                #Expand size of values if needed
                if self.__allsum(self.__prop_shape) > len(self.__values):
                    vals = np.empty(self.__allsum(self.__prop_shape) + 5)
                    for i in xrange(self.__allsum(self.__prop_shape[:-1])):
                        vals[i] = self.__values[i]
                    self.__values = vals    
            
            #Identify property's index, shape and dtype
            p_index = self.__prop_names.index(term)
            shape = self.__prop_shape[p_index]
            dtype = self.__prop_dtype[p_index]            
            start = self.__allsum(self.__prop_shape[:p_index])
            
            #Handle scalars
            if len(shape) == 0 and arg2 is None:
                assert len(arg1.shape) == 0, 'Value must be a scalar'
                if dtype == int:
                    assert arg1.dtype == int,   term + ' must be an integer'
                self.__values[start] = arg1
            
            #Handle vectors
            elif len(shape) == 1 and arg2 is None:
                #if arg1 is an integer return the index value
                if len(arg1.shape) == 0 and arg1.dtype == int:
                    assert arg1 >= 0 and arg1 < shape[0], 'Vector index out of range'
                    return np.array(self.__values[start + arg1], dtype=dtype)
                
                #if shapes match set values
                elif shape == arg1.shape:
                    if dtype == int:
                        assert arg1.dtype == int,   term + ' must be integers'
                    for i in xrange(shape[0]):
                        self.__values[start + i] = arg1[i]
                else:
                    raise TypeError('Invalid arguments')
                    
            #Handle 2D arrays
            elif len(shape) == 2:
                if len(arg1.shape) == 0 and arg1.dtype == int:
                    assert arg1 >= 0 and arg1 < shape[0], 'Array index out of range'
                    if arg2 is None:
                        start = start + arg1 * shape[0]
                        end = start + shape[1]
                        return np.array(self.__values[start:end], dtype=dtype)    
                    elif isinstance(arg2, int):
                        assert arg2 >= 0 and arg2 < shape[1], 'Array index out of range'
                        return np.array(self.__values[start + arg1 * shape[0] + arg2], dtype=dtype)
                    else:
                        raise TypeError('Invalid arguments')
                           
                elif shape == arg1.shape and arg2 is None:   
                    if dtype == int:
                        assert arg1.dtype == int,   term + ' must be integers'
                    for i in xrange(shape[0]):
                        for j in xrange(shape[1]):
                            self.__values[start + i * shape[0] + j] = arg1[i,j]
                else:
                    raise TypeError('Invalid arguments')
            else:
                raise TypeError('Invalid arguments')
            
    def __allsum(self, listy):
        summy = 0
        for item in listy:
            if len(item) == 0:
                summy += 1
            elif len(item) == 1:
                summy += item[0]
            elif len(item) == 2:
                summy += item[0] * item[1]
        return summy
    
    def atype(self, arg1=None):
        #Get or set the atom's type
        output = self.prop('atype', arg1)
        if output is not None:
            return output
    
    def pos(self, arg1=None):
        #Get or set the atom's position
        output = self.prop('pos', arg1)
        if output is not None:
            return output
       
    def prop_list(self):
        #Returns list of assigned per-atom properties
        return deepcopy(self.__prop_names)
