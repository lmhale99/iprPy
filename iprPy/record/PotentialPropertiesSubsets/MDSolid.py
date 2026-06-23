
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class MDSolid(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__structures = pd.DataFrame(columns=self.structurescolumns)
        super().__init__(parent)

    @property
    def structures(self):
        return self.__structures
    
    @structures.setter
    def structures(self, value):
        assert isinstance(value, pd.DataFrame)
        if len(value) > 0:
            self.__structures = value[self.structurescolumns]
        else:
            self.__structures = pd.DataFrame(columns=self.structurescolumns)

    @property
    def structurescolumns(self):
        """list : The column names found in structures"""
        return ['composition', 'prototype', 'a', 'relaxed_crystal_key']

    def load_model(self, model):
        
        structures = []

        if 'md-solid' in model:
            self.exists = True

            for comp_model in model['md-solid'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    prototype = proto_model['prototype']
                    for alat_model in proto_model.aslist('alats'):
                        
                        struct = {}
                        struct['composition'] = composition
                        struct['prototype'] = prototype
                        struct['a'] = alat_model['a']
                        struct['relaxed_crystal_key'] = alat_model['relaxed_crystal_key']
                        structures.append(struct)

            self.__structures = pd.DataFrame(structures)

        
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['md-solid'] = struct_model = DM()

            for composition in np.unique(self.structures.composition):
                comp_structs = self.structures[self.structures.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for prototype in np.unique(comp_structs.prototype):
                    proto_structs = comp_structs[comp_structs.prototype == prototype]
                    
                    proto_model = DM()
                    proto_model['prototype'] = prototype
                    
                    for index in proto_structs.sort_values('a').index:
                        alat_struct = proto_structs.loc[index]
                        
                        alat_model = DM()
                        alat_model['a'] = alat_struct['a']
                        alat_model['relaxed_crystal_key'] = alat_struct['relaxed_crystal_key']
                            
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                struct_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['md_solid'] = self.structures
        return meta