import atomman as am
import numpy as np
from copy import deepcopy
from collections import OrderedDict

class ElasticConstants():
    
    def __init__(self, object=None):
        #initilize ElasticConstants instance
        
        #__c_ij is the 6x6 representation of the elastic constant matrix
        self.__c_ij = np.zeros((6,6), dtype=float)
    
        if object is not None:
            if isinstance(object, (str, unicode)):
                object = am.models.DataModel(object)
            
            #read in DataModel
            if isinstance(object, am.models.DataModel):
                self.read(object)
                
            elif isinstance(object, (list, tuple, np.ndarray)):
                in_array = np.array(object, dtype=float)
                
                if in_array.shape == (6,6):
                    self.Cij(in_array)
                elif in_array.shape == (3,3,3,3):
                    self.Cijkl(in_array)
                else:
                    raise TypeError('Unsupported argument type: array of shape '+str(in_array.shape))
            else:
                raise TypeError('Unsupported argument type: '+str(type(object)))
 
    def __str__(self):
        c = self.Cij()
        for i in xrange(6):
            for j in xrange(6):
                if np.isclose(c[i,j], 0.0, rtol=0, atol=0.01):
                    c[i,j] = 0.0
    
        return '\n'.join(['[[%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (c[0,0], c[0,1], c[0,2], c[0,3], c[0,4], c[0,5]),
                          ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (c[1,0], c[1,1], c[1,2], c[1,3], c[1,4], c[1,5]),
                          ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (c[2,0], c[2,1], c[2,2], c[2,3], c[2,4], c[2,5]),
                          ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (c[3,0], c[3,1], c[3,2], c[3,3], c[3,4], c[3,5]),
                          ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f],' % (c[4,0], c[4,1], c[4,2], c[4,3], c[4,4], c[4,5]),
                          ' [%7.2f, %7.2f, %7.2f, %7.2f, %7.2f, %7.2f]]' % (c[5,0], c[5,1], c[5,2], c[5,3], c[5,4], c[5,5])])
 
    def Cij(self, arg1=None, arg2=None, arg3=None):
        #interact with the 6x6 representation of the elastic constant matrix
        
        #if no arguements, return deepcopy of __c_ij
        if arg1 is None and arg2 is None and arg3 is None:
            return deepcopy(self.__c_ij)
            
        #if arg1 is a 6x6 list/tuple/array, set to __cij
        elif isinstance(arg1, (list, tuple, np.ndarray)) and arg2 is None and arg3 is None:
            in_array = np.array(arg1, dtype=float)
            if in_array.shape == (6,6):
            
                #check symmetry
                for i in xrange(6):
                    for j in xrange(i):
                        assert np.isclose(in_array[i,j], in_array[j,i]), '6x6 matrix not symmetric!' 
                
                self.__c_ij = in_array
            
            else:
                raise TypeError('Unsupported argument type: array of shape '+str(in_array.shape))
            
        #if arg1 and arg2 are integers between 0-5
        elif isinstance(arg1, (int, long)) and isinstance(arg2, (int, long)):
            assert arg1 >= 0 and arg1 < 6, 'index 1 out of range'
            assert arg2 >= 0 and arg2 < 6, 'index 2 out of range'
            i, j = arg1, arg2
            
            #if arg3 is None, return the specified value
            if arg3 is None:
                return deepcopy(self.__c_ij[i, j])
            
            #if arg3 is a number, set the specified value
            elif isinstance(arg3, (int, long, float)):
                self.__c_ij[i,j] = float(arg3)
                self.__c_ij[j,i] = float(arg3)
                
            else:
                raise TypeError('Unsupported argument type: ' + str(type(arg3)))
        else:
            raise TypeError('Unsupported argument types: ' + str(type(arg1)) + ' ' + str(type(arg2)))
                
    def Cijkl(self, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        #interact with the 3x3x3x3 representation of the elastic constant matrix
        
        #if no arguments, return 4D array
        if arg1 is None and arg2 is None and arg3 is None and arg4 is None and arg5 is None:
            c = deepcopy(self.__c_ij)
            return np.array([[[[c[0,0],c[0,5],c[0,4]], [c[0,5],c[0,1],c[0,3]], [c[0,4],c[0,3],c[0,2]]],
                              [[c[5,0],c[5,5],c[5,4]], [c[5,5],c[5,1],c[5,3]], [c[5,4],c[5,3],c[5,2]]],
                              [[c[4,0],c[4,5],c[4,4]], [c[4,5],c[4,1],c[4,3]], [c[4,4],c[4,3],c[4,2]]]], 
                           
                             [[[c[5,0],c[5,5],c[5,4]], [c[5,5],c[5,1],c[5,3]], [c[5,4],c[5,3],c[5,2]]],
                              [[c[1,0],c[1,5],c[1,4]], [c[1,5],c[1,1],c[1,3]], [c[1,4],c[1,3],c[1,2]]],
                              [[c[3,0],c[3,5],c[3,4]], [c[3,5],c[3,1],c[3,3]], [c[3,4],c[3,3],c[3,2]]]],
                             
                             [[[c[4,0],c[4,5],c[4,4]], [c[4,5],c[4,1],c[4,3]], [c[4,4],c[4,3],c[4,2]]],
                              [[c[3,0],c[3,5],c[3,4]], [c[3,5],c[3,1],c[3,3]], [c[3,4],c[3,3],c[3,2]]],
                              [[c[2,0],c[2,5],c[2,4]], [c[2,5],c[2,1],c[2,3]], [c[2,4],c[2,3],c[2,2]]]]])
            
        #if arg1 is a 3x3x3x3 list/tuple/array, convert and set to __c_ij
        elif isinstance(arg1, (list, tuple, np.ndarray)) and arg2 is None and arg3 is None and arg4 is None and arg5 is None:
            c = np.array(arg1, dtype=float)
            if c.shape == (3,3,3,3):
                
                #check symmetry
                indexes = np.array([[0,0], [1,1], [2,2], [1,2], [0,2], [0,1]], dtype=int)
                for ij in range(6):
                    for kl in range(ij, 6):
                        i, j, k, l = indexes[ij,0], indexes[ij,1], indexes[kl,0], indexes[kl,1]
                        assert np.isclose(c[i,j,k,l], c[j,i,k,l])
                        assert np.isclose(c[i,j,k,l], c[j,i,l,k])
                        assert np.isclose(c[i,j,k,l], c[k,l,j,i])
                        assert np.isclose(c[i,j,k,l], c[l,k,j,i])
                        assert np.isclose(c[i,j,k,l], c[i,j,l,k])
                        assert np.isclose(c[i,j,k,l], c[k,l,i,j])
                        assert np.isclose(c[i,j,k,l], c[l,k,i,j])            
        
                self.Cij(np.array([[c[0,0,0,0], c[0,0,1,1], c[0,0,2,2], c[0,0,1,2], c[0,0,0,2], c[0,0,0,1]],
                                   [c[1,1,0,0], c[1,1,1,1], c[1,1,2,2], c[1,1,1,2], c[1,1,0,2], c[1,1,0,1]],
                                   [c[2,2,0,0], c[2,2,1,1], c[2,2,2,2], c[2,2,1,2], c[2,2,0,2], c[2,2,0,1]],
                                   [c[1,2,0,0], c[1,2,1,1], c[1,2,2,2], c[1,2,1,2], c[1,2,0,2], c[1,2,0,1]],
                                   [c[0,2,0,0], c[0,2,1,1], c[0,2,2,2], c[0,2,1,2], c[0,2,0,2], c[0,2,0,1]],
                                   [c[0,1,0,0], c[0,1,1,1], c[0,1,2,2], c[0,1,1,2], c[0,1,0,2], c[0,1,0,1]]]))
        
            else:
                raise TypeError('Unsupported argument type: array of shape '+str(in_array.shape))
                
        #if arg1, arg2, arg3 and ag4 are integers between 0-2 
        elif isinstance(arg1, (int, long)) and isinstance(arg2, (int, long)) and isinstance(arg3, (int, long)) and isinstance(arg4, (int, long)):
            assert arg1 >= 0 and arg1 < 3, 'index 1 out of range'
            assert arg2 >= 0 and arg2 < 3, 'index 2 out of range'
            assert arg3 >= 0 and arg3 < 3, 'index 3 out of range'
            assert arg4 >= 0 and arg4 < 3, 'index 4 out of range'
            c = self.Cijkl()
            i, j, k, l = arg1, arg2, arg3, arg4
            
            #if arg5 is None, return value
            if arg5 is None:
                return deepcopy(c[i,j,k,l])
            
            #if arg5 is a number, set value
            elif isinstance(arg5, (int, long, float)):
                c[i,j,k,l] = arg5
                c[j,i,k,l] = arg5
                c[j,i,l,k] = arg5
                c[k,l,j,i] = arg5
                c[l,k,j,i] = arg5
                c[i,j,l,k] = arg5
                c[k,l,i,j] = arg5
                c[l,k,i,j] = arg5
            self.Cijkl(c)
                
    def transform(self, axes, tol=1e-8):
        #Transforms the elastic constant matrix using the transformation matrix, T.
        
        T = am.tools.axes_check(axes)
        
        Q = np.einsum('km,ln->mnkl', T, T)
        C = np.einsum('ghij,ghmn,mnkl->ijkl', Q, self.Cijkl(), Q)
        C[abs(C) < tol] = 0.0
        
        return ElasticConstants(C)  

    def read(self, datamodel):
        #reads in C information from a DataModel
        if isinstance(datamodel, (str, unicode)):
            datamodel = am.models.DataModel(datamodel)
    
        c_model = datamodel.find('elastic_constants')
        assert len(c_model) == 1, 'Exactly one elastic_constants must be in data model!'
        c_model = c_model[0]
        
        c_dict = OrderedDict()        
        for c_term in c_model['C']:
            ij = c_term['ij']
            c_dict[c_term['ij']] = float(c_term['elasticModulus']['value'])
            
        if len(c_dict) == 3:
            self.cubic(c_dict)
        elif len(c_dict) == 5:
            self.hexagonal(c_dict)
        elif len(c_dict) == 7:
            self.tetragonal(c_dict)
        elif len(c_dict) == 9:
            self.orthorhombic(c_dict)
        else:
            raise ValueError('Crystal system not supported yet')
    
    def cubic(self, c_dict=None, c11=None, c12=None, c44=None):
    #Handles the cubic representation of the elastic constants
        
        #check if c_dict has been supplied
        if c_dict is None:
            
            #return dictionary of cubic constants if no arguements given
            if all_none((c11, c12, c44)):
                c = self.Cij()
                c_dict = OrderedDict()
                c_dict['1 1'] = (c[0,0] + c[1,1] + c[2,2]) / 3
                c_dict['1 2'] = (c[0,1] + c[0,2] + c[1,2]) / 3
                c_dict['4 4'] = (c[3,3] + c[4,4] + c[5,5]) / 3
                return c_dict
            
            #set values if all cubic constants are given
            elif all_not_none((c11, c12, c44)):
                self.Cij( np.array([[c11, c12, c12, 0.0, 0.0, 0.0],
                                    [c12, c11, c12, 0.0, 0.0, 0.0],
                                    [c12, c12, c11, 0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, c44, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, c44, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, 0.0, c44]]) )
            else:
                return TypeError('All necessary constants not given')

        
        else:
            assert all_none((c11, c12, c44)), 'Invalid argument type'
            
            #set values if dictionary is given
            if isinstance(c_dict, dict):
                c11 = c_dict['1 1']
                c12 = c_dict['1 2']
                c44 = c_dict['4 4']
                self.cubic(c11=c11, c12=c12, c44=c44)
            
            #extract and set values if DataModel is given
            elif isinstance(c_dict, (str, unicode, am.models.DataModel)):
                self.cubic(self.read(c_dict))
                
            else:
                return TypeError('Invalid argument type')
    
    def hexagonal(self, c_dict=None, c11=None, c33=None, c12=None, c13=None, c44=None):
    #Handles the hexagonal representation of the elastic constants
    
        #check if c_dict has been supplied
        if c_dict is None:
            
            #return dictionary of hexagonal constants if no arguements given
            if all_none((c11, c33, c12, c13, c44)):
                c = self.Cij()
                c_dict = OrderedDict()
                c_dict['1 1'] = (c[0,0] + c[1,1]) / 2
                c_dict['3 3'] = c[2,2]
                c_dict['1 2'] = (c[0,1] + (c11 - 2*c[5,5])) / 2
                c_dict['1 3'] = (c[0,2] + c[1,2]) / 2
                c_dict['4 4'] = (c[3,3] + c[4,4]) / 2             
                return c_dict
            
            #set values if all hexagonal constants are given
            elif all_not_none((c11, c33, c12, c13, c44)):
                c66 = (c11 - c12) / 2
                self.Cij( np.array([[c11, c12, c13, 0.0, 0.0, 0.0],
                                    [c12, c11, c13, 0.0, 0.0, 0.0],
                                    [c13, c13, c33, 0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, c44, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, c44, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, 0.0, c66]]) )
            else:
                return TypeError('All necessary constants not given')
        else:
            assert all_none((c11, c33, c12, c13, c44)), 'Invalid argument type'
                
        #set values if dictionary is given
            if isinstance(c_dict, dict):
                c11 = c_dict['1 1']
                c33 = c_dict['3 3']
                c12 = c_dict['1 2']
                c13 = c_dict['1 3']
                c44 = c_dict['4 4']
                self.hexagonal(c11=c11, c33=c33, c12=c12, c13=c13, c44=c44)
            
            #extract and set values if DataModel is given
            elif isinstance(c_dict, (str, unicode, am.models.DataModel)):
                self.hexagonal(self.read(c_dict))

            else:
                return TypeError('Invalid argument type')
                
    def tetragonal(self, c_dict=None, c11=None, c33=None, c12=None, c13=None, c16=None, c44=None, c66=None):
    #Handles the tetragonal representation of the elastic constants
    
        #check if c_dict has been supplied
        if c_dict is None:
            
            #return dictionary of tetragonal constants if no arguements given
            if all_none((c11, c33, c12, c13, c16, c44, c66)):
                c = self.Cij()
                c_dict = OrderedDict()
                c_dict['1 1'] = (c[0,0] + c[1,1]) / 2
                c_dict['3 3'] = c[2,2]
                c_dict['1 2'] = c[0,1]
                c_dict['1 3'] = (c[0,2] + c[1,2]) / 2
                c_dict['1 6'] = (c[0,5] - c[1,5]) / 2
                c_dict['4 4'] = (c[3,3] + c[4,4]) / 2
                c_dict['6 6'] = c[5,5]
                return c_dict
            
            #set values if all tetragonal constants are given
            elif all_not_none((c11, c33, c12, c13, c16, c44, c66)):
                self.Cij( np.array([[c11, c12, c13, 0.0, 0.0, c16],
                                    [c12, c11, c13, 0.0, 0.0,-c16],
                                    [c13, c13, c33, 0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, c44, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, c44, 0.0],
                                    [c16,-c16, 0.0, 0.0, 0.0, c66]]) )
            else:
                return TypeError('All necessary constants not given')
        else:
            assert all_none((c11, c33, c12, c13, c16, c44, c66)), 'Invalid argument type'
                
        #set values if dictionary is given
            if isinstance(c_dict, dict):
                c11 = c_dict['1 1']
                c33 = c_dict['3 3']
                c12 = c_dict['1 2']
                c13 = c_dict['1 3']
                c44 = c_dict['4 4']
                self.tetragonal(c11=c11, c33=c33, c12=c12, c13=c13, c44=c44)
            
            #extract and set values if DataModel is given
            elif isinstance(c_dict, (str, unicode, am.models.DataModel)):
                self.tetragonal(self.read(c_dict))

            else:
                return TypeError('Invalid argument type')                
        
    def orthorhombic(self, c_dict=None, c11=None, c22=None, c33=None, c12=None, c13=None, c23=None, c44=None, c55=None, c66=None):
    #Handles the orthorhombic representation of the elastic constants
    
        #check if c_dict has been supplied
        if c_dict is None:
            
            #return dictionary of orthorhombic constants if no arguements given
            if all_none((c11, c22, c33, c12, c13, c23, c44, c55, c66)):
                c = self.Cij()
                c_dict = OrderedDict()
                c_dict['1 1'] = c[0,0]
                c_dict['2 2'] = c[1,1]
                c_dict['3 3'] = c[2,2]
                c_dict['1 2'] = c[0,1]
                c_dict['1 3'] = c[0,2]
                c_dict['2 3'] = c[1,2]
                c_dict['4 4'] = c[3,3]
                c_dict['5 5'] = c[4,4]
                c_dict['6 6'] = c[5,5]                
                return c_dict
            
            #set values if all orthorhombic constants are given
            elif all_not_none((c11, c22, c33, c12, c13, c23, c44, c55, c66)):
                self.Cij( np.array([[c11, c12, c13, 0.0, 0.0, 0.0],
                                    [c12, c22, c23, 0.0, 0.0, 0.0],
                                    [c13, c23, c33, 0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, c44, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, c55, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, 0.0, c66]]) )
            else:
                return TypeError('All necessary constants not given')
        else:
            assert all_none((c11, c22, c33, c12, c13, c23, c44, c55, c66)), 'Invalid argument type'
                
        #set values if dictionary is given
            if isinstance(c_dict, dict):
                c11 = c_dict['1 1']
                c22 = c_dict['2 2']
                c33 = c_dict['3 3']
                c12 = c_dict['1 2']
                c13 = c_dict['1 3']
                c23 = c_dict['2 3']
                c44 = c_dict['4 4']
                c55 = c_dict['5 5']
                c66 = c_dict['6 6']
                self.orthorhombic(c11=c11, c22=c22, c33=c33, c12=c12, c13=c13, c23=c23, c44=c44, c55=c55, c66=c66)
            
            #extract and set values if DataModel is given
            elif isinstance(c_dict, (str, unicode, am.models.DataModel)):
                self.orthorhombic(self.read(c_dict))

            else:
                return TypeError('Invalid argument type')
    
    def model(self, crystal_system='orthorhombic'):
    #returns a DataModel of the elastic constants 
        
        dm = am.models.DataModel()
        dm.data['elastic_constants'] = OrderedDict()
        
        c_dict = self.dict(crystal_system)

        c_formatted = []
        for index, value in c_dict.iteritems():
            c_formatted.append(OrderedDict([('ij',             index),
                                            ('elasticModulus', OrderedDict([('value', value),
                                                                            ('unit',  'GPa')]) )]) )
        
        dm.data['elastic_constants']['C'] = c_formatted
       
        return dm

    def dict(self, crystal_system='orthorhombic'):
        if crystal_system == 'cubic':
            c_dict = self.cubic()
        elif crystal_system == 'hexagonal':
            c_dict = self.hexagonal()
        elif crystal_system == 'tetragonal':
            c_dict = self.tetragonal()
        elif crystal_system == 'orthorhombic':
            c_dict = self.orthorhombic()
        else:    
            raise ValueError('Crystal system not supported yet')
        
        return c_dict

def all_none(terms):
    for term in terms:
        if term is not None:
            return False
    return True

def all_not_none(terms):
    for term in terms:
        if term is None:
            return False
    return True













 