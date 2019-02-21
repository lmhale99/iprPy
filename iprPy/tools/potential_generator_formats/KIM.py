from DataModelDict import DataModelDict as DM

from .. import PotentialGenerator

__all__ = ['KIM']
class KIM(PotentialGenerator):
    def __init__(self, kimid=None, virialstyle='LAMMPSvirial',
                 id=None, key=None, pot_id=None, pot_key=None,
                 units='metal', atom_style='atomic', pair_style='kim',
                 virial='LAMMPSvirial',
                 elements=None, masses=None, symbols=None):

        # Set default values for format
        if pot_id is None:
            pot_id = kimid
        if id is None:
            id = kimid + '--LAMMPS'

        # Set format-specific parameters
        if virial not in ['LAMMPSvirial', 'KIMvirial']:
            raise ValueError("virial must be either 'LAMMPSvirial' or 'KIMvirial'")
        if kimid is None:
            raise ValueError('kimid must be given')
        pair_style_terms=[virial, kimid]

        # Call PotentialGenerator's init
        PotentialGenerator.__init__(self, id=id, key=key, pot_id=pot_id, pot_key=pot_key,
                 units=units, atom_style=atom_style, pair_style=pair_style,
                 pair_style_terms=pair_style_terms,
                 elements=elements, masses=masses, symbols=symbols)
        
    def buildpaircoeff(self):
        paircoeff = DM()
        paircoeff.append('term', DM([('symbols', 'True')]))
        
        return paircoeff 