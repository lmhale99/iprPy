from DataModelDict import DataModelDict as DM
from io import BytesIO

from .records import records_dict

def record_styles():
    """Returns a list of the styles of the loaded calculations."""
    return records_dict.keys()
    
class Record(object):
    """Class for handling different record styles in the same fashion"""
    
    def __init__(self, style, name, content):
        #Check if calculation style exists
        try:
            self.__r_module = records_dict[style]
        except KeyError:
            raise KeyError('No record style ' + style + ' imported')
        
        self.__style = style
        self.__name = name
        self.__content = content
        
    @property
    def style(self):
        return self.__style
        
    @property
    def name(self):
        return self.__name
    
    @property
    def content(self):
        return self.__content        
          
    def todict(self, **kwargs):
        """Converts an xml record to a flat dictionary"""
        
        try: 
            return self.__r_module.todict(self.content, **kwargs)
        except:
            raise AttributeError('Record style ' + self.__style + ' has no attribute todict')
    
    @property
    def schema(self):
        """Returns the path to the .xsd file for the named record."""
        
        try: 
            return self.__r_module.schema()
        except AttributeError:
            raise AttributeError('Record style ' + self.__style + ' has no attribute schema') 