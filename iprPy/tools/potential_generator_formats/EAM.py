from DataModelDict import DataModelDict as DM

from .. import PotentialGenerator

__all__ = ['EAM']
class EAM(PotentialGenerator):
    def __init__(self, paramfiles=None,
                 id=None, key=None, pot_id=None, pot_key=None,
                 units='metal', atom_style='atomic', pair_style='eam',
                 elements=None, masses=None, symbols=None):
        
        # Set default values for format

        # Call PotentialGenerator's init
        PotentialGenerator.__init__(self, id=id, key=key, pot_id=pot_id, pot_key=pot_key,
                                 units=units, atom_style=atom_style, pair_style=pair_style,
                                 elements=elements, masses=masses, symbols=symbols)
        
        # Set format-specific parameters
        if paramfiles is not None:
            if isinstance(paramfiles, str):
                self.paramfiles = [paramfiles]
            else:
                self.paramfiles = list(paramfiles)
            if self.symbols is not None:
                symbols = self.symbols
            else:
                symbols = self.elements
            if len(symbols) != len(self.paramfiles):
                raise ValueError('a paramfile is needed for each symbol/element')
        else:
            raise ValueError('paramfiles must be given')
        
    def buildpaircoeff(self):
        
        if self.symbols is not None:
            symbols = self.symbols
        else:
            symbols = self.elements

        paircoeffs = []
        for symbol, paramfile in zip(symbols, self.paramfiles):
            paircoeff = DM()
            paircoeff['interaction'] = DM([('symbol', [symbol, symbol])])
            paircoeff['term'] = DM([('file', paramfile)])
            paircoeffs.append(paircoeff)
        
        if len(paircoeffs) == 0:
            paircoeffs = paircoeffs[0]
        
        return paircoeffs