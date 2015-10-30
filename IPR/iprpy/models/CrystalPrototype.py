import iprpy
from DataModel import *
import numpy as np
from copy import deepcopy

class CrystalPrototype(DataModel):
    def load(self, file_name):
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
        lattice_type = None
        for ltype in ('cubic', 'tetragonal', 'hexagonal', 'orthorhombic', 'rhombohedral', 'monoclinic', 'triclinic'):
            try:
                lattice = data['crystalPrototype']['lattice'][ltype]
                lattice_type = ltype            
                break
            except:
                pass
        assert lattice_type is not None, 'Invalid lattice information'
        
        #Create ideal box
        if lattice_type == 'cubic':
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = 1.0, c = 1.0)
        
        elif lattice_type == 'tetragonal':
            c_a = lattice['idealParameters']['c_a']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = 1.0, c = c_a)
        
        elif lattice_type == 'hexagonal':
            c_a = lattice['idealParameters']['c_a']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = 1.0, c = c_a, gamma = 120.0)
        
        elif lattice_type == 'orthorhombic':
            b_a = lattice['idealParameters']['b_a']
            c_a = lattice['idealParameters']['c_a']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = b_a, c = c_a)
        
        elif lattice_type == 'rhombohedral':
            alpha = lattice['idealParameters']['alpha']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = 1.0, c = 1.0, alpha = alpha, beta = alpha, gamma = alpha)
        
        elif lattice_type == 'monoclinic':
            b_a = lattice['idealParameters']['b_a']
            c_a = lattice['idealParameters']['c_a']
            beta = lattice['idealParameters']['beta']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = b_a, c = c_a, beta = beta)
        
        elif lattice_type == 'triclinic':
            b_a = lattice['idealParameters']['b_a']
            c_a = lattice['idealParameters']['c_a']
            alpha = lattice['idealParameters']['alpha']
            beta = lattice['idealParameters']['beta']
            gamma = lattice['idealParameters']['gamma']
            self.__datalist['ideal_box'] = iprpy.Box(a = 1.0, b = b_a, c = c_a, alpha = alpha, beta = beta, gamma = gamma)
        
        #Extract atom position information
        self.__datalist['ucell_atoms'] = []
        self.__datalist['nsites'] = 0
        if isinstance(lattice['atomPositions']['site'], list) is False:
            lattice['atomPositions']['site'] = [lattice['atomPositions']['site']]
        for site in lattice['atomPositions']['site']:
            atype = int(site['component'])
            if self.__datalist['nsites'] < atype:
                self.__datalist['nsites'] = atype
            if isinstance(site['atomCoordinates'], list) is False:
                site['atomCoordinates'] = [site['atomCoordinates']]
            for coords in site['atomCoordinates']:
                pos = coords['value']
                self.__datalist['ucell_atoms'].append(iprpy.Atom(atype, pos))
    
    def ucell_atoms(self):
        return self.get('ucell_atoms')
    
    def nsites(self):
        return self.get('nsites')
        
    def ideal_box(self, arg1=None):
        if arg1 is None:
            return self.get('ideal_box')
        else:
            return self.__datalist['ideal_box'].get(arg1)
    
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
        
           
            
    
    