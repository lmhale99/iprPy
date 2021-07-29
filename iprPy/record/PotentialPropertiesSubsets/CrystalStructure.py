
import pandas as pd

from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class CrystalStructure(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.datacolumns)
        self.__protoref = pd.DataFrame()
        super().__init__(parent)

    @property
    def data(self):
        return self.__data

    @property
    def protoref(self):
        return self.__protoref

    @property
    def datacolumns(self):
        """list : The column names found in the associated dataframe"""
        return ['composition', 'prototype', 'method', 'E_pot', 'E_coh',
                'a', 'b', 'c', 'alpha', 'beta', 'gamma']
            
    @property
    def protorefcolumns(self):
        """list : The column names found in the associated dataframe"""
        return ['composition', 'prototype', 'refs']

    def csv(self, composition):
        """str : URL to the csv table of the raw structure content"""
        assert composition in self.data.composition
        return f'{self.parent.webdir}/crystal.{composition}.csv'

    def load_model(self, model):
        
        data = []
        protorefs = []

        if 'crystal-structure' in model:
            self.exists = True          

            for protoref_model in model['crystal-structure'].aslist('prototype-ref-set'):
                protoref = {}
                protoref['composition'] = protoref_model['composition']
                protoref['prototype'] = protoref_model['prototype']
                protoref['references'] = protoref_model.aslist('ref')
                protorefs.append(protoref)
            self.__protoref = pd.DataFrame(protorefs)

            for crystal_model in model['crystal-structure'].aslist('crystal'):
                crystal = {}
                crystal['composition'] = crystal_model['composition']
                crystal['prototype'] = crystal_model['prototype']
                crystal['method'] = crystal_model['method']
                crystal['E_pot'] = uc.value_unit(crystal_model['potential-energy'])
                crystal['E_coh'] = uc.value_unit(crystal_model['cohesive-energy'])
                crystal['a'] = uc.value_unit(crystal_model['a'])
                crystal['b'] = uc.value_unit(crystal_model['b'])
                crystal['c'] = uc.value_unit(crystal_model['c'])
                crystal['alpha'] = float(crystal_model['alpha']['value'])
                crystal['beta'] = float(crystal_model['beta']['value'])
                crystal['gamma'] = float(crystal_model['gamma']['value'])
                data.append(crystal)
            self.__data = pd.DataFrame(data)

        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['crystal-structure'] = DM()
            
            for i in self.protoref.sort_values(['composition', 'prototype']).index:
                protoref = self.protoref.loc[i]
                
                protoref_model = DM()
                protoref_model['composition'] = protoref.composition
                protoref_model['prototype'] = protoref.prototype
                if len(protoref.references) == 1:
                    protoref_model['ref'] = protoref.references[0]
                elif len(protoref.references) > 1:
                    protoref_model['ref'] = protoref.references
                model['crystal-structure'].append('prototype-ref-set', protoref_model)
            
            for i in self.data.sort_values(['composition', 'E_coh']).index:
                crystal = self.data.loc[i]

                crystal_model = DM()
                crystal_model['composition'] = crystal.composition
                crystal_model['prototype'] = crystal.prototype
                crystal_model['method'] = crystal.method
                crystal_model['potential-energy'] = uc.model(crystal.E_pot, 'eV')
                crystal_model['cohesive-energy'] = uc.model(crystal.E_coh, 'eV')
                crystal_model['a'] = uc.model(crystal.a, 'angstrom')
                crystal_model['b'] = uc.model(crystal.b, 'angstrom')
                crystal_model['c'] = uc.model(crystal.c, 'angstrom')
                crystal_model['alpha'] = DM([('value', crystal.alpha), ('unit', 'degree')])
                crystal_model['beta'] = DM([('value', crystal.beta), ('unit',' degree')])
                crystal_model['gamma'] = DM([('value', crystal.gamma), ('unit', 'degree')])

                model['crystal-structure'].append('crystal', crystal_model)

    def metadata(self, meta):
        meta['protorefs'] = self.protoref
        meta['crystals'] = self.data
        return meta        