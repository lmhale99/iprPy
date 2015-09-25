from iprp.models import DataModel
from iprp import AtomType
from copy import deepcopy
import os

class Potential(DataModel):
    def __init__(self, file_name = None, pot_dir = None):
        self.__datalist = {}
        self.__datalist['id'] = ''
        
        DataModel.__init__(self, file_name = file_name)
        
        if pot_dir != None:
            self.__datalist['pot_dir'] = pot_dir
        else:
            self.__datalist['pot_dir'] = ''
    
    def __str__(self):
        return self.get('id')
    
    def load(self, file_name):
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        
        #Set basic properties
        self.__datalist['id'] = data['interatomicPotentialImplementationLAMMPS']['potentialID']['descriptionIdentifier']
        self.__datalist['units'] = data['interatomicPotentialImplementationLAMMPS']['units']
        self.__datalist['atom_style'] = data['interatomicPotentialImplementationLAMMPS']['atom_style']
        
        #Read pair_style information
        self.__pair_style = data['interatomicPotentialImplementationLAMMPS']['pair_style']
        try:
            test = self.__pair_style['term']
            if isinstance(test, list) == False:
                self.__pair_style['term'] = [self.__pair_style['term']]
        except:
            pass
        
        #Set AtomType properties
        self.__datalist['atomtypes'] = []
        ainfo = data['interatomicPotentialImplementationLAMMPS']['atom']
        if isinstance(ainfo, list) == False:
            ainfo = [ainfo]
        for atom in ainfo:
            atomtype = AtomType(0)
            for name, value in atom.iteritems():
                atomtype.set(name, value)
            if atomtype.get('mass') == 0.0:
                atomtype.set('mass', None)
            self.__datalist['atomtypes'].append(atomtype)
            
        #Read pair_coeff information
        self.__pair_coeff = data['interatomicPotentialImplementationLAMMPS']['pair_coeff']
        if isinstance(self.__pair_coeff,list) == False:
            self.__pair_coeff = [self.__pair_coeff]       
        for coeff_line in self.__pair_coeff:
            if isinstance(coeff_line['term'],list) == False:
                coeff_line['term'] = [coeff_line['term']]    
    
    def get(self, term=None, safe=True):
        if term == None:
            value = DataModel.get(self, safe=safe)
        else:
            try:
                value = self.__datalist[term]
            except:
                value = None
        if safe:
            return deepcopy(value)
        else:
            return value    
    
    def elements(self):
        elist = []
        for atomtype in self.__datalist['atomtypes']:
            elist.append(str(atomtype))
        return elist
        
    #Returns pair_style and pair_coeff lines associated with a given list of elements
    def coeff(self, elements = None):
        #if no elements supplied use all for potential
        if elements == None:
            elements = self.elements()
        elif isinstance(elements, list) == False:
            elements = [elements]
        
        #Generate pair_style info
        style = 'pair_style ' + str(self.__pair_style['type'])
        try:
            term = self.__pair_terms(self.__pair_style['term'], elements)
        except:
            term = '\n'
        style += term 
        
        #if only one pair_coeff set is defined for a potential
        if len(self.__pair_coeff) == 1:
            coeff = 'pair_coeff * *'
            coeff += self.__pair_terms(self.__pair_coeff[0]['term'],elements)
            
        #if multiple pair_coeff sets are listed
        elif len(self.__pair_coeff) > 1:
            
            #Check if cross terms are included
            try:
                val = self.__pair_style['cross']
                if val == 'False':
                    cross = False
                else:
                    cross = True
            except:
                cross = True                    
                
            coeff = ''
            #if cross terms are included
            if cross:
                for i in xrange(len(elements)):
                    e_i = elements[i]
                    for j in xrange(i,len(elements)):
                        e_j = elements[j]
                        for pair_set in self.__pair_coeff:
                            p_i = pair_set['interaction']['element'][0]
                            p_j = pair_set['interaction']['element'][1]
                            if (e_i == p_i and e_j == p_j) or (e_i == p_j and e_j == p_i):
                                coeff += 'pair_coeff %i %i'%(i+1,j+1)
                                if i == j:
                                    coeff += self.__pair_terms(pair_set['term'],[e_i])
                                else:
                                    coeff += self.__pair_terms(pair_set['term'],[e_i,e_j])
            #if no cross terms (eg. eam)
            else:
                for i in xrange(len(elements)):
                    e_i = elements[i]
                    for pair_set in self.__pair_coeff:
                        p_i = pair_set['interaction']['element'][0]
                        p_j = pair_set['interaction']['element'][1]
                        if (e_i == p_i == p_j):
                            coeff += 'pair_coeff %i %i'%(i+1,i+1)
                            coeff += self.__pair_terms(pair_set['term'],[e_i])
        return style + coeff
    
    def masses(self, elements=None):
        mlist = []
        if elements == None:
            elements = self.elements()
        elif isinstance(elements, list) == False:
            elements = [elements]
        
        for el in elements:
            for atomtype in self.__datalist['atomtypes']:
                if el == atomtype.get('element'):
                    mlist.append(atomtype.get('mass'))
                    break
        if len(elements) == len(mlist):
            return mlist
        else:
            raise ValueError('Not all elements found!')
                 
    
    #Utility function used by self.coeff() for composing pair_coeff lines from the terms
    def __pair_terms(self, terms, elements):
        #elist = element name (and symbol) from "atom" section of potential file
        line = ''
        for term in terms:
            for ttype, tval in term.iteritems():
                if ttype == 'option': 
                    line += ' ' + tval
                    
                elif ttype == 'file':
                    line += ' ' + str(os.path.join(self.__datalist['pot_dir'],tval))
                    
                elif ttype == 'symbolsList' and tval == 'True':
                    uelements = []
                    for e in elements:
                        new = True
                        for u in uelements:
                            if e == u:
                                new = False
                                break
                        if new:
                            uelements.append(e)
                    for u in uelements:
                        for atomtype in self.__datalist['atomtypes']:
                            if u == atomtype.get('element'):
                                sym = atomtype.get('symbol')
                                if sym == None:
                                    sym = u
                                break 
                        line += ' ' + sym
                        
                elif ttype == 'symbols' and tval == 'True':
                    for e in elements:
                        for atomtype in self.__datalist['atomtypes']:
                            if e == atomtype.get('element'):
                                sym = atomtype.get('symbol')
                                if sym == None:
                                    sym = e
                                break    
                        line += ' ' + sym
                        
        return line + '\n'    
        
        
        