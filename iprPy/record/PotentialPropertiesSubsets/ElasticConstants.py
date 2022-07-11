import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class ElasticConstants(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.datacolumns)
        super().__init__(parent)

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        assert isinstance(value, pd.DataFrame)
        self.__data = value[self.datacolumns]

    @property
    def datacolumns(self):
        """list : The column names found in the associated dataframe"""
        return ['composition', 'prototype', 'a', 'strainrange', 'straindirection', 'Cij']

    def csv(self, composition):
        """str : URL to the csv table of the raw structure content"""
        assert composition in self.data.composition
        return f'{self.parent.webdir}/elastic.{composition}.csv'

    def load_model(self, model):
        
        cijs = []

        if 'elastic-constants' in model:
            self.exists = True          

            for comp_model in model['elastic-constants'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    prototype = proto_model['prototype']
                    for alat_model in proto_model.aslist('alats'):
                        a = alat_model['a']
                        for m in alat_model.aslist('measurement'):
                            strain = float(m['strain'])
                            Cij = np.array([[m['C11'], m['C12'], m['C13'], m['C14'], m['C15'], m['C16']],
                                            [m['C21'], m['C22'], m['C23'], m['C24'], m['C25'], m['C26']],
                                            [m['C31'], m['C32'], m['C33'], m['C34'], m['C35'], m['C36']],
                                            [m['C41'], m['C42'], m['C43'], m['C44'], m['C45'], m['C46']],
                                            [m['C51'], m['C52'], m['C53'], m['C54'], m['C55'], m['C56']],
                                            [m['C61'], m['C62'], m['C63'], m['C64'], m['C65'], m['C66']]])
                            measurement = {}
                            measurement['composition'] = composition
                            measurement['prototype'] = prototype
                            measurement['a'] = a
                            measurement['strainrange'] = abs(strain)
                            if strain > 0:
                                measurement['straindirection'] = 'positive'
                            else:
                                measurement['straindirection'] = 'negative'
                            measurement['Cij'] = Cij
                            cijs.append(measurement)
            self.__data = pd.DataFrame(cijs)
                            
        else:
            self.exists = False

    def build_model(self, model):
        if self.exists is True:
            model['elastic-constants'] = ec_model = DM()

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
                        
                        for i in alat_records.sort_values(['strainrange', 'straindirection']).index:
                            series = alat_records.loc[i]
                            measurement = DM()
                            if series.straindirection == 'positive':
                                measurement['strain'] = '+%s' %series.strainrange
                            elif series.straindirection == 'negative':
                                measurement['strain'] = '-%s' %series.strainrange
                            else:
                                raise ValueError('Unknown straindirection')

                            for i in range(6):
                                for j in range(6):
                                    measurement[f'C{i+1}{j+1}'] = '%.3f' % series.Cij[i,j]
                            
                            alat_model.append('measurement', measurement)
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                ec_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['cijs'] = self.data
        return meta        