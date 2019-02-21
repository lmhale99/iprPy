raise NotImplementedError('pair_style and pair_coeff builders not set yet')

from DataModelDict import DataModelDict as DM

from .. import PotentialGenerator

__all__ = ['PAIR']
class PAIR(PotentialGenerator):
    def __init__(self, paramfiles=None,
                 id=None, key=None, pot_id=None, pot_key=None,
                 units='metal', atom_style='atomic', pair_style='eam',
                 pair_style_terms=None,
                 elements=None, masses=None, symbols=None):
        
        # Set default values for format

        # Call PotentialGenerator's init
        PotentialGenerator.__init__(self, id=id, key=key, pot_id=pot_id, pot_key=pot_key,
                                 units=units, atom_style=atom_style, pair_style=pair_style,
                                 pair_style_terms=None,
                                 elements=elements, masses=masses, symbols=symbols)
        
        # Set format-specific parameters
        if paramfiles is not None:
            if isinstance(paramfiles, str):
                self.paramfiles = [paramfiles]
            else:
                self.paramfiles = list(paramfiles)
        else:
            raise ValueError('paramfiles must be given')
        
    def buildpaircoeff(self):
        paircoeff = DM()
        paircoeff.append('term', DM([('file', self.paramfiles)]))
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff

    def supported_pair_styles(self):
        return []