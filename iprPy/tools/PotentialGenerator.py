# Standard libraries
import uuid

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

class PotentialGenerator(object):
    """
    Template class for generating potential_LAMMPS records for different pair styles.
    """

    def __init__(self, id=None, key=None, pot_id=None, pot_key=None,
                 units=None, atom_style=None, pair_style=None,
                 pair_style_terms=None,
                 elements=None, masses=None, symbols=None):        
        
        if id is not None:
            self.id = id
        else:
            raise ValueError('id must be given')
        
        if key is not None:
            self.key = key
        else:
            self.key = str(uuid.uuid4())

        if pot_id is not None:
            self.pot_id = pot_id
        else:
            try:
                self.pot_id = id[:id.index('--LAMMPS')]
            except:
                self.pot_id = id

        if pot_key is not None:
            self.pot_key = pot_key
        else:
            self.pot_key = str(uuid.uuid4())

        if units is not None:
            self.units = units
        else:
            raise ValueError('units must be given')
        
        if atom_style is not None:
            self.atom_style = atom_style
        else:
            raise ValueError('atom_style must be given')

        if symbols is None and elements is None:
            raise ValueError('elements and/or symbols must be given')
        
        if isinstance(symbols, str):
            symbols = [symbols]
        elif symbols is not None:
            symbols = list(symbols)
        self.symbols = symbols

        if isinstance(elements, str):
            elements = [elements]
        elif elements is not None:
            elements = list(elements)
        self.elements = elements

        if masses is not None:
            try:
                masses = list(masses)
            except:
                masses = [masses]
        self.masses = masses

        if pair_style is not None:
            self.pair_style = pair_style
        else:
            raise ValueError('pair_style must be given')
        
        if pair_style_terms is not None:
            if isinstance(pair_style_terms, (str, bytes)):
                self.pair_style_terms = [pair_style_terms]
            else:
                try:
                    self.pair_style_terms = list(pair_style_terms)
                except:
                    self.pair_style_terms = [pair_style_terms]
        else:
            self.pair_style_terms = []

    def build(self):

        # Initialize model
        model = DM()
        model['potential-LAMMPS'] = DM()
        model['potential-LAMMPS']['key'] = self.key
        model['potential-LAMMPS']['id'] = self.id
        model['potential-LAMMPS']['potential'] = DM()
        model['potential-LAMMPS']['potential']['key'] = self.pot_key
        model['potential-LAMMPS']['potential']['id'] = self.pot_id
        model['potential-LAMMPS']['units'] = self.units
        model['potential-LAMMPS']['atom_style'] = self.atom_style
    
        for atom in self.iteratoms():
            model['potential-LAMMPS'].append('atom', atom)
        
        model['potential-LAMMPS']['pair_style'] = self.buildpairstyle()
        model['potential-LAMMPS']['pair_coeff'] = self.buildpaircoeff()
    
        return model

    @property
    def symbollist(self):
        if self.symbols is not None:
            return ' '.join(self.symbols)
        else:
            return ' '.join(self.elements)

    def iteratoms(self):
        if self.symbols is not None:
            symbols = self.symbols
        else:
            symbols = [None for i in range(len(self.elements))]
        
        if self.elements is not None:
            elements = self.elements
        else:
            elements = [None for i in range(len(self.symbols))]
        
        if self.masses is not None:
            masses = self.masses
        else:
            masses = [None for i in range(len(elements))]

        assert len(symbols) == len(elements), 'incompatible symbols, elements lengths'
        assert len(symbols) == len(masses), 'incompatible symbols, masses lengths'

        for element, symbol, mass in zip(elements, symbols, masses):
            atom = DM()
            if symbol is not None:
                atom['symbol'] = symbol
            if element is not None:
                atom['element'] = element
            if mass is not None:
                atom['mass'] = mass
            yield atom

    def buildpairstyle(self):
        pairstyle = DM()
        pairstyle['type'] = self.pair_style
        
        for term in self.pair_style_terms:
            if isinstance(term, (int, float)):
                pairstyle.append('term', DM([('parameter', term)]))
            else:
                pairstyle.append('term', DM([('option', str(term))]))
        return pairstyle

    def buildpaircoeff(self):
        paircoeff = None

        return paircoeff