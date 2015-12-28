import atomman as am
from DataModel import DataModel
import numpy as np
from copy import deepcopy
from mag import mag

class Prototype(DataModel):
    #Class for handling the crystalPrototype xml/json data model

    def load(self, file_name):
    #Load a crystal prototype file
    
        #Read file and create datalist
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        self.__datalist = {}
        
        #Extract prototype ids
        self.__id = {}
        for id_type, id_name in data['crystalPrototype']['crystalProtoypeID'].iteritems():
            self.__id[id_type] = str(id_name)
            self.__datalist[id_type] = str(id_name)
        
        #Extract prototype information
        self.__info = {}
        for info_type, info_name in data['crystalPrototype']['crystalProtoypeInfo'].iteritems():
            self.__info[info_type] = str(info_name)
            self.__datalist[info_type] = str(info_name)
        
        #Identify the lattice type 
        crystal_system = None
        for ltype in ('cubic', 'tetragonal', 'hexagonal', 'orthorhombic', 'rhombohedral', 'monoclinic', 'triclinic'):
            try:
                lattice = data['crystalPrototype']['lattice'][ltype]
                crystal_system = ltype            
                break
            except:
                pass
        assert crystal_system is not None, 'Invalid lattice information'
        self.__info['crystal_system'] = crystal_system
        self.__datalist['crystal_system'] = crystal_system
        
        #Read in ideal lattice parameters
        self.__ideal_params = {}
        try:
            params = lattice['idealParameters']
            for param_name, param_value in params.iteritems():
                self.__ideal_params[param_name] = param_value
        except:
            pass
        
        #Extract atom position information
        self.__atoms = []
        if isinstance(lattice['atomPositions']['site'], list) is False:
            lattice['atomPositions']['site'] = [lattice['atomPositions']['site']]
        for site in lattice['atomPositions']['site']:
            atype = int(site['component'])
            if isinstance(site['atomCoordinates'], list) is False:
                site['atomCoordinates'] = [site['atomCoordinates']]
            for coords in site['atomCoordinates']:
                pos = coords['value']
                self.__atoms.append(am.Atom(atype, pos))
    
    def ucell(self, a=None, b=None, c=None, alpha=None, beta=None, gamma=None):
    #Generate a unit cell based on the ideal or supplied lattice parameters
        sys_type = self.__datalist['crystal_system']
        
        if sys_type == 'cubic':
            if a is None:
                assert b is None and c is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a
            if c is None:
                c = a
            assert a == b and a == c, 'cubic lattice parameters must be equal'
            
            assert alpha is None or np.isclose(alpha, 90), 'cubic angles must be 90'
            assert beta  is None or np.isclose(beta,  90), 'cubic angles must be 90'
            assert gamma is None or np.isclose(gamma, 90), 'cubic angles must be 90'
        
        elif sys_type == 'tetragonal':
            if a is None:
                assert b is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a
            assert a == b, 'tetragonal parameters a and b must be equal'
            if c is None:
                c = a * self.__ideal_params['c_a']
                
            assert alpha is None or np.isclose(alpha, 90), 'tetragonal angles must be 90'
            assert beta  is None or np.isclose(beta,  90), 'tetragonal angles must be 90'
            assert gamma is None or np.isclose(gamma, 90), 'tetragonal angles must be 90'
            
        elif sys_type == 'hexagonal':
            if a is None:
                assert b is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a
            assert a == b, 'hexagonal parameters a and b must be equal'
            if c is None:
                c = a * self.__ideal_params['c_a']
                
            assert alpha is None or np.isclose(alpha, 90), 'hexagonal angle alpha must be 90'
            assert beta  is None or np.isclose(beta,  90), 'hexagonal angle beta must be 90'
            assert gamma is None or np.isclose(gamma, 120), 'hexagonal angle gamma must be 120'
        
        elif sys_type == 'orthorhombic':
            if a is None:
                assert b is None and c is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a * self.__ideal_params['b_a']
            if c is None:
                c = a * self.__ideal_params['c_a']
            
            assert alpha is None or np.isclose(alpha, 90), 'orthorhombic angles must be 90'
            assert beta  is None or np.isclose(beta,  90), 'orthorhombic angles must be 90'
            assert gamma is None or np.isclose(gamma, 90), 'orthorhombic angles must be 90'
        
        elif sys_type == 'rhombohedral' or sys_type == 'trigonal':
            if a is None:
                assert b is None and c is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a
            if c is None:
                c = a
            assert a == b and a == c, 'rhombohedral lattice parameters must be equal'
            
            if alpha is None:
                alpha = self.__ideal_params['alpha']
            if beta is None:
                beta = alpha
            if gamma is None:
                gamma = alpha
            assert alpha < 120, 'Non-standard rhombohedral angle'
            assert alpha == beta and alpha == gamma, 'rhombohedral angles must be equal'
        
        elif sys_type == 'monoclinic':
            if a is None:
                assert b is None and c is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a * self.__ideal_params['b_a']
            if c is None:
                c = a * self.__ideal_params['c_a']
            
            if beta is None:
                beta = self.__ideal_params['beta']
            assert beta > 90, 'Non-standard monoclinic angle'
            assert alpha is None or np.isclose(alpha, 90), 'orthorhombic angles must be 90'
            assert gamma is None or np.isclose(gamma, 90), 'orthorhombic angles must be 90'
        
        elif sys_type == 'triclinic':
            if a is None:
                assert b is None and c is None, 'define lattice parameters in order'
                a = 1.0
            if b is None:
                b = a * self.__ideal_params['b_a']
            if c is None:
                c = a * self.__ideal_params['c_a']

            if alpha is None:
                alpha = self.__ideal_params['alpha']
            if beta is None:
                beta =  self.__ideal_params['beta']
            if gamma is None:
                gamma = self.__ideal_params['gamma']
        
        return am.System(box = am.Box(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma), 
                         atoms = self.__atoms, 
                         scale = True)
    
    def r_a(self):
    #Calculate the shortest radial distance between atoms wrt a
        cell = self.ucell()
        
        minimum_r = min(cell.box('a'), cell.box('b'), cell.box('c'))
        for i in xrange(cell.natoms()):
            for j in xrange(i):
                rdist = mag(cell.dvect(i,j))
                if rdist < minimum_r:
                    minimum_r = rdist
        return minimum_r
    
    def get(self, term = None, safe = True):
        if term == None:
            value = DataModel.get(self, safe=safe)
        else:
            try:
                value = self.__datalist[term]
            except:
                value = None
        if safe:
            return deepcopy(value)
        else:
            return value
    
    def isid(self, test):
        for id_type, id_name in self.__id.iteritems():
            if id_name == test:
                return True
        return False

    def isinfo(self, test):
        for info_type, info_name in self.__info.iteritems():
            if info_name == test:
                return True
        return False        
        
           
            
    
    