
from DataModelDict import DataModelDict as DM

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist


class EvsRScan(PotentialsPropertiesSubset):

    def __init__(self, parent):
        self.__compositions = []
        super().__init__(parent)

    def table(self, composition):
        """str : URL to the txt table of the diatom plot"""
        assert composition in self.compositions
        return f'{self.parent.webdir}/EvsR.{composition}.txt'

    def png(self, composition):
        """str : URL to the png of the diatom plot"""
        assert composition in self.compositions
        return f'{self.parent.webdir}/EvsR.{composition}.png'

    def html(self, composition):
        """str : URL to the interactive diatom plot page"""
        assert composition in self.compositions
        return f'{self.parent.webdir}/EvsR.{composition}.html'

    @property
    def compositions(self):
        return self.__compositions

    def load_model(self, model):
        
        if 'cohesive-energy-scan' in model:
            self.exists = True            
            self.__compositions = aslist(model['cohesive-energy-scan'].get('composition', []))
        else:
            self.exists = False
            self.__compositions = []

    def build_model(self, model):
        if self.exists is True:
            model['cohesive-energy-scan'] = DM()
            if len(self.compositions) == 1:
                model['cohesive-energy-scan']['composition'] = self.compositions[0]
            elif len(self.compositions) > 1:
                model['cohesive-energy-scan']['composition'] = self.compositions

    def metadata(self, meta):
        meta['E_vs_r_scans'] = self.compositions
        return meta