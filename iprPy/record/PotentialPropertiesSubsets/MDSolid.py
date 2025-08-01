
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class MDSolid(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__structureplot = pd.DataFrame(columns=self.structureplotcolumns)
        super().__init__(parent)

    @property
    def structureplot(self):
        return self.__structureplot
    
    @structureplot.setter
    def structureplot(self, value):
        assert isinstance(value, pd.DataFrame)
        if len(value) > 0:
            self.__structureplot = value[self.structureplotcolumns]
        else:
            self.__structureplot = pd.DataFrame(columns=self.structureplotcolumns)

    @property
    def structureplotcolumns(self):
        """list : The column names found in structureplot"""
        return ['composition', 'prototype', 'a', 'name', 'png']


    def load_model(self, model):
        
        plots = []

        if 'mdsolid' in model:
            self.exists = True

            for comp_model in model['mdsolid']['plot'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    prototype = proto_model['prototype']
                    for alat_model in proto_model.aslist('alats'):
                        a = alat_model['a']
                        
                        for p in alat_model.aslist('plot'):
                            plot = {}
                            plot['composition'] = composition
                            plot['prototype'] = prototype
                            plot['a'] = a
                            plot['name'] = p['name']
                            plot['png'] = f'{self.parent.webdir}/{p["file"]}'
                            plots.append(plot)

            self.__plot = pd.DataFrame(plots)

        
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['mdsolid'] = DM()
            model['mdsolid']['plot'] = plot_model = DM()

            for composition in np.unique(self.plot.composition):
                comp_plots = self.plot[self.plot.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for prototype in np.unique(comp_plots.prototype):
                    proto_plots = comp_plots[comp_plots.prototype == prototype]
                    
                    proto_model = DM()
                    proto_model['prototype'] = prototype
                    
                    for alat in np.unique(proto_plots.a):
                        alat_plots = proto_plots[proto_plots.a == alat]
                        
                        alat_model = DM()
                        alat_model['a'] = alat

                        for i in alat_plots.index:
                            series = alat_plots.loc[i]

                            plot = DM()
                            plot['name'] = series['name']
                            plot['file'] = series.png.replace(f'{self.parent.webdir}/', '')
                            alat_model.append('plot', plot)
                            
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                plot_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['mdsolidplots'] = self.plot
        return meta