
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class DislMono(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__cores = pd.DataFrame(columns=self.corescolumns)
        super().__init__(parent)

    @property
    def cores(self):
        return self.__cores
    
    @cores.setter
    def cores(self, value):
        assert isinstance(value, pd.DataFrame)
        if len(value) > 0:
            self.__cores = value[self.corescolumns]
        else:
            self.__cores = pd.DataFrame(columns=self.corescolumns)

    @property
    def corescolumns(self):
        """list : The column names found in cores"""
        return ['composition', 'dislocation_id', 'key']

    def load_model(self, model):
        
        cores = []

        if 'dislocation-monopole' in model:
            self.exists = True

            for comp_model in model['dislocation-monopole'].aslist('compositions'):
                composition = comp_model['composition']
                for core_model in comp_model.aslist('cores'):
                    core = {}
                    core['composition'] = composition
                    core['dislocation_id'] = core_model['dislocation-id']
                    core['key'] = core_model['calc-key']
                    cores.append(core)

            self.__cores = pd.DataFrame(cores)

        
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['dislocation-monopole'] = struct_model = DM()

            for composition in np.unique(self.cores.composition):
                comp_cores = self.cores[self.cores.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for index in comp_cores.index:
                    disl_core = comp_cores.loc[index]

                    core_model = DM()
                    core_model['dislocation-id'] = disl_core['dislocation_id']
                    core_model['calc-key'] = disl_core['key']
                        
                    comp_model.append('cores', core_model)
                struct_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['disl_mono'] = self.cores
        return meta
