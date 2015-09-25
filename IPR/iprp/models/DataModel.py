from dict_2_xml import *
from xml_2_dict import *
from collections import OrderedDict
import json
from copy import deepcopy

class DataModel:
    def __init__(self, file_name = None):
        if file_name != None:
            self.load(file_name)
        else:
            self.__data = OrderedDict()
    
    def load(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'r') as f:
                self.__data = json.load(f, object_pairs_hook = OrderedDict) 
                
        elif file_name[-4:] == '.xml':
            with open(file_name, 'r') as f:
                self.__data = xml_2_dict(f.read())
        
        else:
            raise ValueError('Unsupported file type for DataModel load')
    
    def dump(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'w') as f:
                f.write(json.dumps( self.__data, indent = 4, separators = (',',': ') ))
        
        elif file_name[-4:] == '.xml':
            with open(file_name,'w') as f:
                f.write(dict_2_xml(self.__data))
        
        else:
            raise ValueError('Unsupported file type for DataModel dump')
    
    def get(self, safe = True):
        if safe:
            return deepcopy(self.__data)
        else:
            return self.__data