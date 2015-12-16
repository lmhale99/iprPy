from atomman.tools import DataModel
from copy import deepcopy
from collections import OrderedDict
from atomman.tools.elemental_values import el_tag, get_mass
import os

class Potential(DataModel):
    def __init__(self, file_name = None, pot_dir = None):
        self.__tag = None
        self.__units = None
        self.__atom_style = None
        if pot_dir is None:
            self.__pot_dir = ''
        else:
            self.__pot_dir = pot_dir
        self.__atom_data = OrderedDict()
        self.__pair_style = OrderedDict()
        self.__pair_coeff = OrderedDict()
                
        DataModel.__init__(self, file_name = file_name)
        
    def __str__(self):
        return self.__tag
    
    def load(self, file_name):
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        
        #Set basic properties
        self.__tag =        data['interatomicPotentialImplementationLAMMPS']['potentialID']['descriptionIdentifier']
        self.__units =      data['interatomicPotentialImplementationLAMMPS']['units']
        self.__atom_style = data['interatomicPotentialImplementationLAMMPS']['atom_style']
        
        #Set atomic properties
        if isinstance(data['interatomicPotentialImplementationLAMMPS']['atom'], list) is False:
            data['interatomicPotentialImplementationLAMMPS']['atom'] = [data['interatomicPotentialImplementationLAMMPS']['atom']]
        
        for atom in data['interatomicPotentialImplementationLAMMPS']['atom']:
            #Check if element is listed
            try:
                test = atom['element']
                if isinstance( atom['element'], int):
                    atom['element'] = el_tag( atom['element'] )
            #If no element is listed, symbol and mass must be
            except:
                try:
                    test = atom['symbol']
                    test = atom['mass']
                except:
                    raise KeyError("Error reading Potential's atomic info: mass and symbol are needed if element is not given!")
            
            #Check if symbol is listed.  If not, make symbol = element
            try:
                test = atom['symbol']
            except:
                atom['symbol'] = atom['element']
            
            #Check if mass is listed.  If not, set to standard value of element
            try:
                mass_check = atom['mass']
            except:
                atom['mass'] = get_mass(atom['element'])
            assert isinstance(atom['mass'], float), 'Mass needs to be a number!'
            
            self.__atom_data[ atom['symbol'] ] = atom
        
        #Read pair_style information
        self.__pair_style = data['interatomicPotentialImplementationLAMMPS']['pair_style']
        try:
            test = self.__pair_style['type']
        except:
            raise KeyError('Error reading Potential: No pair_style type defined!')
        
        try:
            test = self.__pair_style['term']
            if isinstance(test, list) is False:
                self.__pair_style['term'] = [self.__pair_style['term']]
        except:
            self.__pair_style['term'] = []
        
        #Read pair_coeff information
        self.__pair_coeff = data['interatomicPotentialImplementationLAMMPS']['pair_coeff']
        if isinstance(self.__pair_coeff, list) is False:
            self.__pair_coeff = [self.__pair_coeff]       
        for coeff_line in self.__pair_coeff:
            try:
                if isinstance(coeff_line['interaction']['element'], list) is False:
                    coeff_line['interaction']['element'] = [coeff_line['interaction']['element']]
            except:    
                coeff_line['interaction'] = {'element': ['*','*']}
            try:
                if isinstance(coeff_line['term'], list) is False:
                    coeff_line['term'] = [coeff_line['term']]                 
            except:
                coeff_line['term'] = []
    
    def elements(self, arg = None):
        if arg is None:
            el_list = []
            for sym, data in self.__atom_data.iteritems():
                el_list.append(data['element'])
            return el_list
        else:
            if isinstance(arg, (list, tuple)):
                el_list = []
                for sym in arg:
                    try:
                        el_list.append(self.__atom_data[sym]['element'])
                    except:
                        el_list.append(None)
                return el_list
            else:
                try:
                    return self.__atom_data[arg]['element']
                except:
                    return None
    
    def masses(self, arg = None):
        if arg is None:
            el_list = []
            for sym, data in self.__atom_data.iteritems():
                el_list.append(data['mass'])
            return el_list
        else:
            if isinstance(arg, (list, tuple)):
                el_list = []
                for sym in arg:
                    try:
                        el_list.append(self.__atom_data[sym]['mass'])
                    except:
                        el_list.append(None)
                return el_list
            else:
                try:
                    return self.__atom_data[arg]['mass']
                except:
                    return None
    
    def symbols(self):
        el_list = []
        for sym, data in self.__atom_data.iteritems():
            el_list.append(sym)
        return el_list
    
    def units(self):
        return self.__units
        
    def atom_style(self):
        return self.__atom_style
    
    #Returns mass, pair_style and pair_coeff LAMMPS command lines associated with a given list of element symbols
    def pair_info(self, symbols = None):
        #if no symbols supplied use all for potential
        if symbols is None:
            symbols = self.symbols()
        elif isinstance(symbols, list) is False:
            symbols = [symbols]
        
        #Generate mass lines
        mass = ''
        for i in xrange(len(symbols)):
            mass += 'mass %i %f' % ( i+1, self.masses(symbols[i]) ) + '\n'
        mass +='\n'
        
        #Generate pair_style line
        style = 'pair_style ' + self.__pair_style['type'] + self.__pair_terms(self.__pair_style['term']) + '\n'        
       
        #Generate pair_coeff lines
        coeff = ''
        for coeff_line in self.__pair_coeff:
            
            #Always include coeff lines that act on all atoms in the system
            if coeff_line['interaction']['element'] == ['*', '*']:
                coeff_symbols = self.symbols()
                coeff += 'pair_coeff * *' + self.__pair_terms(coeff_line['term'], symbols, coeff_symbols) + '\n'
                continue
            
            #Many-body potentials will contain a symbols term
            many = False
            for term in coeff_line['term']:
                if 'symbols' in term:
                    many = True
                    break
                                                    
            #Treat as a many-body potential
            if many:
                coeff_symbols = coeff_line['interaction']['element']
                coeff += 'pair_coeff * *' + self.__pair_terms(coeff_line['term'], symbols, coeff_symbols) + '\n'
                
            #Treat as pair potential
            else:
                coeff_symbols = coeff_line['interaction']['element']
                assert len(coeff_symbols) == 2,     'Pair potential interactions need two listed elements'
                
                #Classic eam style is a special case
                if self.__pair_style['type'] == 'eam':
                    assert coeff_symbols[0] == coeff_symbols[1], 'Only i==j interactions allowed for eam style'
                    for i in xrange( len(symbols) ):
                        if symbols[i] == coeff_symbols[0]:
                            coeff += 'pair_coeff %i %i' % (i + 1, i + 1) + self.__pair_terms(coeff_line['term'], symbols, coeff_symbols) + '\n'
                
                #All other pair potentials
                else:
                    for i in xrange( len(symbols) ):
                        for j in xrange( i, len(symbols) ):
                            if (symbols[i] == coeff_symbols[0] and symbols[j] == coeff_symbols[1]) or (symbols[i] == coeff_symbols[1] and symbols[j] == coeff_symbols[0]):
                               
                                coeff += 'pair_coeff %i %i' % (i + 1, j + 1) + self.__pair_terms(coeff_line['term'], symbols, coeff_symbols) + '\n'

        return mass + style + coeff
    
    #Utility function used by self.coeff() for composing pair_coeff lines from the terms
    def __pair_terms(self, terms, system_symbols = [], coeff_symbols = []):
        line = ''
        for term in terms:
            for ttype, tval in term.iteritems():
                if ttype == 'option': 
                    line += ' ' + str(tval)
                    
                elif ttype == 'file':
                    line += ' ' + str( os.path.join(self.__pot_dir, tval) )
                    
                elif ttype == 'symbolsList' and tval == 'True':
                    for coeff_symbol in coeff_symbols:
                        if coeff_symbol in system_symbols:
                            line += ' ' + coeff_symbol
                        
                elif ttype == 'symbols' and tval == 'True':
                    for system_symbol in system_symbols:
                        if system_symbol in coeff_symbols:
                            line += ' ' + system_symbol
                        else:
                            line += ' NULL'
                            
        return line     
        
        
        