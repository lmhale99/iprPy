
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class Melt(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.datacolumns)
        super().__init__(parent)

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, value):
        assert isinstance(value, pd.DataFrame)
        if len(value) > 0:
            self.__data = value[self.datacolumns]
        else:
            self.__data = pd.DataFrame(columns=self.datacolumns)

    @property
    def datacolumns(self):
        """list : The column names found in data"""
        return ['composition', 'prototype', 'Tmelt', 'Tmelt_stderr']

    def load_model(self, model):
        
        data = []

        if 'melt' in model:
            self.exists = True

            for comp_model in model['melt'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    
                    dat = {}
                    dat['composition'] = composition
                    dat['prototype'] = proto_model['prototype']
                    dat['Tmelt'] = proto_model['Tmelt']
                    dat['Tmelt_stderr'] = proto_model['Tmelt-stderr']
                    data.append(dat)

            self.__data = pd.DataFrame(data)

        
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['melt'] = struct_model = DM()

            for composition in np.unique(self.data.composition):
                comp_data = self.data[self.data.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for index in comp_data.sort_values('prototype').index:
                    proto_data = comp_data.loc[index]
                    
                    proto_model = DM()
                    proto_model['prototype'] = proto_data['prototype']
                    proto_model['Tmelt'] = proto_data['Tmelt']
                    proto_model['Tmelt-stderr'] = proto_data['Tmelt_stderr']
                    
                    comp_model.append('prototypes', proto_model)
                struct_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['melt'] = self.data
        return meta