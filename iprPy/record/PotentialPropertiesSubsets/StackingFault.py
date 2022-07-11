
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class StackingFault(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__data = pd.DataFrame(columns=self.datacolumns)
        self.__plot = pd.DataFrame(columns=self.plotcolumns)
        super().__init__(parent)

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, value):
        assert isinstance(value, pd.DataFrame)
        self.__data = value[self.datacolumns]
    
    @property
    def plot(self):
        return self.__plot

    @plot.setter
    def plot(self, value):
        assert isinstance(value, pd.DataFrame)
        self.__plot = value[self.plotcolumns]

    @property
    def datacolumns(self):
        """list : The column names found in data"""
        return ['composition', 'prototype', 'a', 'plane', 'measurement', 'value']

    @property
    def plotcolumns(self):
        """list : The column names found in plot"""
        return ['composition', 'prototype', 'a', 'plane', 'name', 'png', 'json']

    def load_model(self, model):
        
        data = []
        plots = []

        if 'stacking-faults' in model:
            self.exists = True          
            for comp_model in model['stacking-faults'].aslist('compositions'):
                composition = comp_model['composition']
                for proto_model in comp_model.aslist('prototypes'):
                    prototype = proto_model['prototype']
                    for alat_model in proto_model.aslist('alats'):
                        a = alat_model['a']
                        for plane_model in proto_model.aslist('planes'):
                            plane = plane_model['plane']

                            for p in plane_model.aslist('plot'):
                                plot = {}
                                plot['composition'] = composition
                                plot['prototype'] = prototype
                                plot['a'] = a
                                plot['plane'] = plane
                                plot['name'] = p['name']
                                plot['png'] = f'{self.parent.webdir}/{p["file"]}'
                                plot['json'] = f'{self.parent.webdir}/{plane["json"]}'
                                plots.append(plot)

                            for m in plane_model.aslist('measurement'):
                                measurement = {}
                                measurement['composition'] = composition
                                measurement['prototype'] = prototype
                                measurement['a'] = a
                                measurement['plane'] = plane
                                measurement['measurement'] = m['name']
                                measurement['value'] = m['value']
                                data.append(measurement)
            self.__data = pd.DataFrame(data)
            self.__plot = pd.DataFrame(plots)
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['stacking-faults'] = ec_model = DM()

            for composition in np.unique(self.plot.composition):
                comp_plots = self.plot[self.plot.composition == composition]
                comp_results = self.data[self.data.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for prototype in np.unique(comp_plots.prototype):
                    proto_plots = comp_plots[comp_plots.prototype == prototype]
                    proto_results = comp_results[comp_results.prototype == prototype]
                    proto_model = DM()
                    proto_model['prototype'] = prototype
                    
                    for alat in np.unique(proto_plots.a):
                        alat_plots = proto_plots[proto_plots.a == alat]
                        alat_results = proto_results[proto_results.a == alat]
                        alat_model = DM()
                        alat_model['a'] = alat

                        for plane in np.unique(alat_plots.plane):
                            plane_plots = alat_plots[alat_plots.plane == plane]
                            plane_results = alat_results[alat_results.plane == plane]
                            plane_model = DM()
                            plane_model['plane'] = plane

                            for i in plane_plots.index:
                                series = plane_plots.loc[i]

                                if 'json' not in plane_model:
                                    plane_model['json'] = series.json.replace(f'{self.parent.webdir}/', '')

                                plot = DM()
                                plot['name'] = series['name']
                                plot['file'] = series.png.replace(f'{self.parent.webdir}/', '')
                                plane_model.append('plot', plot)
                            
                            for i in plane_results.index:
                                series = plane_results.loc[i]
                                measurement = DM()
                                measurement['name'] = series.measurement
                                measurement['value'] = '%.2f' % series.value
                                plane_model.append('measurement', measurement)

                            alat_model.append('planes', plane_model)
                        proto_model.append('alats', alat_model)
                    comp_model.append('prototypes', proto_model)
                ec_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['stackingfaults'] = self.data
        meta['stackingfaultplots'] = self.plot
        return meta        