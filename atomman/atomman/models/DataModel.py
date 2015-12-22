import xmltodict
import json
from collections import OrderedDict

class DataModel():
    def __init__(self, file_name=None):
        
        if file_name is not None:
            self.load(file_name)
        else:
            self.data = OrderedDict()
    
    def load(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'r') as f:
                self.data = json.load(f, object_pairs_hook = OrderedDict) 
                
        elif file_name[-4:] == '.xml':
            with open(file_name, 'r') as f:
                self.data = xmltodict.parse(f.read())
        
        else:
            raise ValueError('Unsupported file type for DataModel')
    
    def find(self, key):
        return [val for val in gen_dict_extract(key, self.data)]
        
    def dump(self, file_name):
        if file_name[-5:] == '.json':
            with open(file_name,'w') as f:
                f.write(json.dumps( self.data, indent = 4, separators = (',',': ') ))
                
        elif file_name[-4:] == '.xml':
            with open(file_name, 'w') as f:
                f.write(xmltodict.unparse(self.data, pretty=True))
        
        else:
            raise ValueError('Unsupported file type for DataModel')

    def ismodel(self, key):
        if key in self.data:
            return True
        else:
            return False
    
def gen_dict_extract(key, var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result