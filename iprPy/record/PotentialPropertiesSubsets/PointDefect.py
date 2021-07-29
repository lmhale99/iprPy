
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class PointDefect(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.dfcolumns)
        super().__init__(parent)

    @property
    def data(self):
        return self.__data

    @property
    def dfcolumns(self):
        """list : The column names found in the associated dataframe"""
        return ['composition', 'prototype', 'a', 'pointdefect', 'E_f', 'pij']

    def csv(self, composition):
        """str : URL to the csv table of the raw structure content"""
        assert composition in self.data.composition
        return f'{self.parent.webdir}/pointdefect.{composition}.csv'

    def load_model(self, model):
        
        ptds = []

        if 'point-defects' in model:
            self.exists = True          
            for comp_model in model['point-defects'].aslist('compositions'):
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
                            measurement['pointdefect'] = m['pointdefect']
                            measurement['E_f'] = m['energy']
                            measurement['pij'] = np.array([[m['p11'], m['p12'], m['p13']],
                                                           [m['p12'], m['p22'], m['p23']],
                                                           [m['p13'], m['p23'], m['p33']]])
                            ptds.append(measurement)
            self.__data = pd.DataFrame(ptds)
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['point-defects'] = ec_model = DM()

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
                            measurement['pointdefect'] = series.pointdefect
                            measurement['energy'] = series.E_f
                            measurement['p11'] = series.pij[0,0]
                            measurement['p22'] = series.pij[1,1]
                            measurement['p33'] = series.pij[2,2]
                            measurement['p12'] = series.pij[0,1]
                            measurement['p13'] = series.pij[0,2]
                            measurement['p23'] = series.pij[1,2]
                            
                            alat_model.append('measurement', measurement)
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                ec_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['pointdefects'] = self.data
        return meta        