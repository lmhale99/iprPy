from DataModel import DataModel
import numpy as np
from copy import deepcopy
from collections import OrderedDict

class DislocationMonopole(DataModel):
    def load(self, file_name):
        #Read file and create datalist
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        self.__datalist = OrderedDict()
        self.__datalist['list'] = []
        
        self.__datalist['prototype'] = data['dislocationMonopoleList']['crystalPrototype']
        self.__datalist['Nye_cutoff'] = data['dislocationMonopoleList']['nyeTensorParameters']['nearestNeighborCutoff']['value'] 
        self.__datalist['Nye_angle'] = data['dislocationMonopoleList']['nyeTensorParameters']['maximumBondAngle']['value'] 
        self.__datalist['Nye_p'] = []
        sites = data['dislocationMonopoleList']['nyeTensorParameters']['referenceNeighborVectors']['site'] 
        if isinstance(sites, list) == False:
            sites = [sites]
        for site in sites:
            p = []
            for set in site['neighborVectors']:
                p.append(set['value'])
            self.__datalist['Nye_p'].append(np.array(p))
        
        defects = data['dislocationMonopoleList']['dislocationMonopole']
        if isinstance(defects, list) == False:
            defects = [defects]
        
        for defect in defects:
            tag = str(defect['dislocationMonopoleInformation']['tag'])
            self.__datalist[tag] = dset = OrderedDict()
            self.__datalist['list'].append(tag)
            dset['burgers_vector'] = np.array(defect['dislocationMonopoleInformation']['burgersVector'])
            dset['slip_plane'] = np.array(defect['dislocationMonopoleInformation']['slipPlane'])
            dset['line_direction'] = np.array(defect['dislocationMonopoleInformation']['lineDirection'])
            dset['character'] = np.array(defect['dislocationMonopoleInformation']['character'])
            
            dset['burgers'] = np.array(defect['simulationParameters']['burgers'])
            dset['axes'] = np.array([defect['simulationParameters']['crystallographicAxes']['x-axis'],
                                     defect['simulationParameters']['crystallographicAxes']['y-axis'],
                                     defect['simulationParameters']['crystallographicAxes']['z-axis']])
            dset['shift'] = np.array(defect['simulationParameters']['shift'])
            dset['zwidth'] = np.array(defect['simulationParameters']['width'])
                
                
            
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

