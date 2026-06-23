
from DataModelDict import DataModelDict as DM

from .PotentialsPropertiesSubset import PotentialsPropertiesSubset
from ...tools import aslist


class MDLiquid(PotentialsPropertiesSubset):

    def __init__(self, parent):
        self.__compositions = []
        super().__init__(parent)

    @property
    def compositions(self):
        return self.__compositions

    def load_model(self, model):
        if 'md-liquid' in model:           
            self.__compositions = aslist(model['md-liquid'].get('composition', []))
            if len(self.compositions) > 0:
                self.exists = True
        else:
            self.__compositions = []

    def build_model(self, model):
        if self.exists is True:
            model['md-liquid'] = DM()
            if len(self.compositions) == 1:
                model['md-liquid']['composition'] = self.compositions[0]
            elif len(self.compositions) > 1:
                model['md-liquid']['composition'] = self.compositions

    def metadata(self, meta):
        meta['md_liquid'] = self.compositions
        return meta