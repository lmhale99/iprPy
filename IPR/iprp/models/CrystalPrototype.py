import iprp
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
        
        #Extract ideal lattice parameters for orthorhombic cell
        a_a = data['crystalPrototype']['orthorhombicCell']['latticeParameters']['value'][0]
        b_a = data['crystalPrototype']['orthorhombicCell']['latticeParameters']['value'][1]
        c_a = data['crystalPrototype']['orthorhombicCell']['latticeParameters']['value'][2]
        self.__datalist['box'] = np.array([[0.0, a_a, 0.0], 
                                           [0.0, b_a, 0.0], 
                                           [0.0, c_a, 0.0]])
        self.__datalist['lat_mult'] = np.array([a_a, b_a, c_a])
        
        #Extract unit cell information
        self.__datalist['ucell'] = []
        self.__datalist['nsites'] = 0
        for site in data['crystalPrototype']['orthorhombicCell']['atomPositions']['site']:
                atype = int(site['component'])
                if self.__datalist['nsites'] < atype:
                    self.__datalist['nsites'] = atype
                for coords in site['atomCoordinates']:
                    coord = coords['value']
                    self.__datalist['ucell'].append(iprp.Atom(atype, coord))
    
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
        
           
            
    
    