from DataModel import DataModel
import numpy as np
from collections import OrderedDict
from copy import deepcopy

class PointDefect(DataModel):
    def load(self, file_name):
        #Read file and create datalist
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        self.__datalist = OrderedDict()
        self.__datalist['list'] = []
        
        self.__datalist['prototype'] = data['pointDefectList']['crystalPrototype']
        
        if isinstance(data['pointDefectList']['pointDefect'], list):
            defects = data['pointDefectList']['pointDefect']
        else:
            defects = [data['pointDefectList']['pointDefect']]
        
        for defect in defects:
            tag = str(defect['pointDefectID']['tag'])
            self.__datalist[tag] = OrderedDict()
            self.__datalist['list'].append(tag)
            self.__datalist[tag]['name'] = str(defect['pointDefectID']['name'])
            self.__datalist[tag]['tag'] = tag
            self.__datalist[tag]['parameters'] = []
            
            if isinstance(defect['parameters'], list):
                parameters = defect['parameters']
            else:
                parameters = [defect['parameters']]
            
            for param in parameters:
                pset = OrderedDict()
                try:
                    pset['ptdtype'] = str(param['defectType'])
                except:
                    pset['ptdtype'] = None
                try:
                    pset['atype'] = int(param['atype'])
                except:
                    pset['atype'] = None
                try:
                    pset['pos'] = np.array(param['coordinates']['value'])
                except:
                    pset['pos'] = None
                try:
                    pset['d'] = np.array(param['dumbbellVector']['value'])
                except:
                    pset['d'] = None
                self.__datalist[tag]['parameters'].append(pset)
            
    def get(self, term1 = None, term2 = None, safe = True):
        if term1 == None:
            value = DataModel.get(self, safe=safe)
        elif term2 == None:
            try:
                value = self.__datalist[term1]
            except:
                value = None
        else:
            try:
                value = self.__datalist[term1][term2]
            except:
                value = None
        if safe:
            return deepcopy(value)
        else:
            return value
    
    def list(self):
        return self.__datalist['list']
        
           
            
    
    