from DataModelDict import DataModelDict as DM

from .. import PotentialGenerator

__all__ = ['LIBRARY']
class LIBRARY(PotentialGenerator):
    def __init__(self, libfile=None, paramfile=None,
                 id=None, key=None, pot_id=None, pot_key=None,
                 units='metal', atom_style='atomic', pair_style='meam',
                 pair_style_terms=None,
                 elements=None, masses=None, symbols=None):
        
        # Set default values for format

        # Call PotentialGenerator's init
        PotentialGenerator.__init__(self, id=id, key=key, pot_id=pot_id, pot_key=pot_key,
                                 units=units, atom_style=atom_style, pair_style=pair_style,
                                 pair_style_terms=None,
                                 elements=elements, masses=masses, symbols=symbols)
        
        # Set format-specific parameters
        if libfile is not None:
            self.libfile = libfile
        else:
            raise ValueError('libfile must be given')
        if paramfile is not None:
            self.paramfile = paramfile
        else:
            self.paramfile = 'NULL'
        
    def buildpaircoeff(self):
        paircoeff = DM()
        paircoeff.append('term', DM([('file', self.libfile)]))
        paircoeff.append('term', DM([('option', self.symbollist)]))
        paircoeff.append('term', DM([('file', self.paramfile)]))
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff