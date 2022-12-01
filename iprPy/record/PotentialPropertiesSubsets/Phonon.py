
import pandas as pd
import numpy as np
from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist

class Phonon(PotentialsPropertiesSubset):
    def __init__(self, parent):
        self.__phononplot = pd.DataFrame(columns=self.phononplotcolumns)
        self.__thermoplot = pd.DataFrame(columns=self.thermoplotcolumns)
        super().__init__(parent)

    @property
    def phononplot(self):
        return self.__phononplot
    
    @phononplot.setter
    def phononplot(self, value):
        assert isinstance(value, pd.DataFrame)
        self.__phononplot = value[self.phononplotcolumns]
    
    @property
    def thermoplot(self):
        return self.__thermoplot

    @thermoplot.setter
    def thermoplot(self, value):
        assert isinstance(value, pd.DataFrame)
        self.__thermoplot = value[self.thermoplotcolumns]

    @property
    def phononplotcolumns(self):
        """list : The column names found in phononplot"""
        return ['composition', 'prototype', 'a', 'name', 'png']

    @property
    def thermoplotcolumns(self):
        """list : The column names found in thermoplot"""
        return ['composition', 'name', 'html', 'png', 'csv']

    def load_model(self, model):
        
        phononplots = []
        thermoplots = []

        if 'phonons' in model:
            self.exists = True

            for comp_model in model['phonons']['plot'].aslist('compositions'):
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
                            phononplots.append(plot)

            self.__phononplot = pd.DataFrame(phononplots)

            for comp_model in model['phonons']['thermo'].aslist('compositions'):
                composition = comp_model['composition']
                
                for p in comp_model.aslist('plot'):
                    plot = {}
                    plot['composition'] = composition
                    plot['prototype'] = prototype
                    plot['a'] = a
                    plot['name'] = p['name']
                    plot['png'] = f'{self.parent.webdir}/{p["file"]}'
                    plot['html'] = f'{self.parent.webdir}/{p["html"]}'
                    plot['csv'] = f'{self.parent.webdir}/{p["csv"]}'
                    thermoplots.append(plot)

            self.__thermoplot = pd.DataFrame(thermoplots)
        
        else:
            self.exists = False
            
    def build_model(self, model):
        if self.exists is True:
            model['phonons'] = DM()
            model['phonons']['plot'] = plot_model = DM()
            model['phonons']['thermo'] = thermo_model = DM()

            for composition in np.unique(self.phononplot.composition):
                comp_plots = self.phononplot[self.phononplot.composition == composition]
                
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

            for composition in np.unique(self.thermoplot.composition):
                comp_plots = self.thermoplot[self.thermoplot.composition == composition]
                
                # Build PotentialProperties data
                comp_model = DM()
                comp_model['composition'] = composition
                
                for i in comp_plots.index:
                    series = comp_plots.loc[i]

                    plot = DM()
                    plot['name'] = series['name']
                    plot['file'] = series.png.replace(f'{self.parent.webdir}/', '')
                    plot['html'] = series.html.replace(f'{self.parent.webdir}/', '')
                    plot['csv'] = series.csv.replace(f'{self.parent.webdir}/', '')
                    comp_model.append('plot', plot)
                            
                thermo_model.append('compositions', comp_model)

    def metadata(self, meta):
        meta['phononplots'] = self.phononplot
        meta['phononthermoplots'] = self.thermoplot
        return meta