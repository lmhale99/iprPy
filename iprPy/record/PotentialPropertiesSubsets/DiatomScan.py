
from .PotentialsPropertiesSubset import PotentialsPropertiesSubset

class DiatomScan(PotentialsPropertiesSubset):

    def table(self):
        """str : URL to the txt table of the diatom plot"""
        return f'{self.parent.webdir}/diatom.txt'

    def png(self):
        """str : URL to the png of the diatom plot"""
        return f'{self.parent.webdir}/diatom.png'

    def shortpng(self):
        """str : URL to the png of the short-range diatom plot"""
        return f'{self.parent.webdir}/diatom_short.png'

    def html(self):
        """str : URL to the interactive diatom plot page"""
        return f'{self.parent.webdir}/diatom.html'

    def shorthtml(self):
        """str : URL to the interactive short-range diatom plot page"""
        return f'{self.parent.webdir}/diatom_short.html'

    def load_model(self, model):
        hasresults = model.get('diatom-scan', 'no')
        self.exists = hasresults == 'yes'

    def build_model(self, model):
        if self.exists is True:
            model['diatom-scan'] = 'yes'

    def metadata(self, meta):
        meta['diatom'] = self.exists
        return meta
