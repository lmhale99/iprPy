from collections import OrderedDict
from elemental_values import el_tag, get_mass

class AtomType:
    #initialize Atom instance
    def __init__(self, element, mass=None):
        self.__set_element(element)
        self.__set_mass(mass)
        self.__prop = OrderedDict() 

    #Printing AtomType returns element name
    def __str__(self):
        return self.__element 
        
    #Set per-atom property value according to property name 
    def set(self, name, value):
        if name == 'element':
            self.__set_element(value)
        elif name == 'mass':
            self.__set_mass(value)   
        else:
            self.__prop[name] = value
    
    #Get per-atom property value using property name    
    def get(self, name):
        if name == 'element':
            return self.__element
        elif name == 'mass':
            return self.__mass
        else:
            try:
                return self.__prop[name]
            except:
                return None        
    
    #Return list of assigned per-atom properties            
    def list(self):
        l = ['element', 'mass']
        for k,v in self.__prop.iteritems():
            l.append(k)
        return l
    
    #Internal function for setting element name
    def __set_element(self, value):
        if isinstance(value, int):
            value = el_tag(value)
        self.__element = value
    
    #Internal function for setting mass
    def __set_mass(self, value=None):
        if value == None:
            try:
                value = get_mass(self.__element)
            except:
                value = 0.0
        try:
            value = float(value)
        except:
            value = 0.0
        self.__mass = value


   