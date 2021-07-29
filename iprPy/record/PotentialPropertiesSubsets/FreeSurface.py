
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class FreeSurface(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.dfcolumns)
        super().__init__(parent)

    @property
    def data(self):
        return self.__data

    @property
    def dfcolumns(self):
        """list : The column names found in the associated dataframe"""
        return ['composition', 'prototype', 'a', 'surface', 'E_f']

    def csv(self, composition):
        """str : URL to the csv table of the raw structure content"""
        assert composition in self.data.composition
        return f'{self.parent.webdir}/freesurface.{composition}.csv'

    def load_model(self, model):
        
        surfs = []

        if 'free-surfaces' in model:
            self.exists = True          
            for comp_model in model['free-surfaces'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    prototype = proto_model['prototype']
                    for alat_model in proto_model.aslist('alats'):
                        a = alat_model['a']
                        for m in alat_model.aslist('measurement'):
                            measurement = {}
                            measurement['composition'] = composition
                            measurement['prototype'] = prototype
                            measurement['a'] = a
                            measurement['surface'] = m['surface']
                            measurement['E_f'] = m['energy']
                            surfs.append(measurement)
            self.__data = pd.DataFrame(surfs)
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['free-surfaces'] = ec_model = DM()

            for composition in np.unique(self.data.composition):
                comp_results = self.data[self.data.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for prototype in np.unique(comp_results.prototype):
                    proto_results = comp_results[comp_results.prototype == prototype]
                    proto_model = DM()
                    proto_model['prototype'] = prototype
                    
                    for alat in np.unique(proto_results.a):
                        alat_records = proto_results[proto_results.a == alat]
                        alat_model = DM()
                        alat_model['a'] = alat
                        
                        for i in alat_records.sort_values(['E_f']).index:
                            series = alat_records.loc[i]
                            measurement = DM()
                            measurement['surface'] = series.surface
                            measurement['energy'] = series.E_f
                            
                            alat_model.append('measurement', measurement)
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                ec_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['freesurfaces'] = self.data
        return meta        