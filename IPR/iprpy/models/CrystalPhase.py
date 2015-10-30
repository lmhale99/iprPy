import iprp
from DataModel import *
import numpy as np
from copy import deepcopy
from collections import OrderedDict
import uuid

class CrystalPhase(DataModel):
    def __init__(self, file_name=None):
        self.__datalist = OrderedDict()
        
        DataModel.__init__(self, file_name = file_name)
        try:
            test = self.__datalist['hash']
        except:
            self.__datalist['hash'] = str(uuid.uuid4())
    
    #Read in information from json/xml file
    def load(self, file_name):
        #Load data and read unique calculation hash ID
        DataModel.load(self, file_name)
        data = DataModel.get(self)
        self.__datalist['hash'] = str(data['calculationCrystalPhase']['calculationID'])
        
        #Set potential name
        pot_name = str(data['calculationCrystalPhase']['potentialID']['descriptionIdentifier'])
        self.__datalist['pot_name'] = pot_name
        
        sim = data['calculationCrystalPhase']['simulation']
        
        #Read atoms and quantities
        self.__datalist['elements'] = []
        list_elements = sim['substance']['composition']['constituent']
        if isinstance(list_elements,list) == False:
            list_elements = [list_elements]
        for element in list_elements:
            self.__datalist['elements'].append({'element': str(element['element']),
                                                'quantity':int(element['quantity']['value'])})
                                                
        self.__datalist['chem_formula'] = sim['substance']['chemicalFormula']                                        
        
        #Read crystal prototype name        
        self.__datalist['prototype'] = sim['crystalPrototype']
        
        #Read cohesive energy    
        self.__datalist['ecoh'] = sim['cohesiveEnergy']['value'] 

        #Read lattice constants
        self.__datalist['alat'] = np.array(sim['latticeConstants']['value'])

        #Read bulk modulus
        self.__datalist['b_mod'] = sim['elasticConstants']['bulkModulus']['value']
        
        #Read elastic constant matrix
        cij = np.zeros((6,6))
        for cval in sim['elasticConstants']['C']:
            ij = cval['ij'].split()
            i = int(ij[0])-1
            j = int(ij[1])-1
            cij[i,j] = cval['elasticModulus']['value']
            cij[j,i] = cval['elasticModulus']['value'] 
        self.__datalist['cij'] = cij
        
        #Read cohesive energy relation plot data
        rvalues = []
        avalues = []
        evalues = []
        for point in sim['cohesiveEnergyRelation']['point']:
            rvalues.append(point['r']['value'])
            avalues.append(point['a']['value'])
            evalues.append(point['cohesiveEnergy']['value'])
        self.__datalist['EvsR'] = {'r': rvalues, 'a':avalues, 'Ecoh':evalues}
    
    #Create json/xml file
    def dump(self, file_name):
        self.build()
        DataModel.dump(self,file_name)
    
    #Get values or access json dictionary
    def get(self, term1 = None, safe=False):
        if term1 == None:
            value = DataModel.get(self, safe=safe)
        elif term1 != None:                
            try:
                value = self.__datalist[term1]
            except:
                value = None
        
        if safe:
            return deepcopy(value)
        else:
            return value

    #Set the interatomic potential name
    def set_pot_name(self, name):
        self.__datalist['pot_name'] = name  

    #Set the calculation results
    def set_sim_data(self, elements, proto, ecoh, alat, b_mod, cij):
        #Count how many atoms are at each prototype site
        if len(elements) == proto.get('nsites'):
            
            self.__datalist['elements'] = []
            self.__datalist['chem_formula'] = ''
            
            for i in xrange(len(elements)):
                count = 0
                for atom in proto.get('ucell'):
                    if atom.get('type') == i+1:
                        count += 1
                self.__datalist['elements'].append({'element': elements[i],
                                                    'quantity': count})
                self.__datalist['chem_formula'] += elements[i]
                if count > 1:
                    self.__datalist['chem_formula'] += str(count)
        else:
            raise ValueError('# of elements != # of prototype sites')
        
        self.__datalist['prototype'] = proto.get('tag')
        self.__datalist['ecoh'] = ecoh
        self.__datalist['alat'] = alat
        self.__datalist['b_mod'] = b_mod
        self.__datalist['cij'] = cij
             
    #Set the E vs r plot data
    def set_E_vs_r_data(self, rvalues, avalues, evalues):
        if len(rvalues) == len(avalues) == len(evalues):
            self.__datalist['EvsR'] = {'r': rvalues, 'a':avalues, 'Ecoh':evalues}
        else:
            raise ValueError('length of E vs r lists not equal')
    
    #Constructs the json data model using the current dictionary values     
    def build(self):
        #Create pointer to current json data model
        data = DataModel.get(self, safe = False)
        
        #Clear data model and add id information
        data['calculationCrystalPhase'] = OrderedDict()
        data['calculationCrystalPhase']['calculationID'] = self.get('hash')
        data['calculationCrystalPhase']['potentialID'] = OrderedDict()
        data['calculationCrystalPhase']['potentialID']['descriptionIdentifier'] = self.get('pot_name')
        
        data['calculationCrystalPhase']['simulation'] = sim = OrderedDict()
        
        #Add simulation information
        sim['substance'] = OrderedDict()
                    
        #Add composition information          
        constituents = []   
        for element in self.get('elements'):
            elinfo = OrderedDict()
            elinfo['element'] = element['element']
            elinfo['quantity'] = OrderedDict([( 'value', element['quantity'] ),
                                              ( 'unit', 'number of atoms' )]) 
            constituents.append(elinfo)
                        
        if len(constituents) == 1:    
            sim['substance']['composition'] = OrderedDict([( 'constituent', constituents[0] )])
        elif len(constituents) > 1:
            sim['substance']['composition'] = OrderedDict([( 'constituent', constituents )])
        
        sim['substance']['chemicalFormula'] = self.get('chem_formula')
        
        
        #Add prototype name
        sim['crystalPrototype'] = self.get('prototype')
                    
        #Add cohesive energy
        sim['cohesiveEnergy'] = OrderedDict([( 'value', self.get('ecoh') ),
                                             ( 'unit', 'eV' )]) 
      
        #Add lattice constants
        sim['latticeConstants'] = OrderedDict()
        alat = [float(str(self.get('alat')[0])), 
                float(str(self.get('alat')[1])), 
                float(str(self.get('alat')[2]))]
                
        sim['latticeConstants']['value'] = alat
        sim['latticeConstants']['unit'] = 'Angstrom'  
        
        #Add elastic constants
        sim['elasticConstants'] = OrderedDict()
        
        #Add bulk modulus
        sim['elasticConstants']['bulkModulus'] = OrderedDict([( 'value', self.get('b_mod')),
                                                              ( 'unit', 'GPa' )])
        #Add cij matrix
        sim['elasticConstants']['C'] = []
        cij = OrderedDict([( 'ij', '1 1' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[0,0])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij', '2 2' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[1,1])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij', '3 3' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[2,2])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij', '1 2' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[0,1])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)            
        cij = OrderedDict([( 'ij', '1 3' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[0,2])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij', '2 3' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[1,2])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij','4 4' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[3,3])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)            
        cij = OrderedDict([( 'ij', '5 5' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[4,4])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        cij = OrderedDict([( 'ij', '6 6' ),
                           ( 'elasticModulus',
                               OrderedDict([( 'value', float(str(self.get('cij')[5,5])) ),
                                            ( 'unit', 'GPa' )]) )])
        sim['elasticConstants']['C'].append(cij)
        
        #Add cohesive energy relation
        sim['cohesiveEnergyRelation'] = OrderedDict()
        points = []
        rvals = self.get('EvsR')['r']
        avals = self.get('EvsR')['a']
        evals = self.get('EvsR')['Ecoh']
        
        for i in xrange(len(rvals)):
            point = OrderedDict()
            point['r'] = OrderedDict([( 'value', rvals[i] ),
                                      ( 'unit', 'Angstrom' )])
            point['a'] = OrderedDict([( 'value', avals[i] ),
                                      ( 'unit', 'Angstrom' )])
            point['cohesiveEnergy'] = OrderedDict([( 'value', evals[i] ),
                                                   ( 'unit', 'eV' )])
            points.append(point)
        
        if len(points) == 1:
            sim['cohesiveEnergyRelation']['point'] = points[0]
        else:
            sim['cohesiveEnergyRelation']['point'] = points
        
            
