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
    
    def __str__(self):
        return self.name + ' (' + self.style + ')'
    
    @property
    def style(self):
        return self.__style
        
    @property
    def name(self):
        return self.__name
    
    @property
    def content(self):
        return self.__content
        
    @content.setter
    def content(self, value):
        self.__content = value
          
    def todict(self, **kwargs):
        """Converts an xml record to a flat dictionary"""
        
        try: 
            todict = self.__r_module.todict
        except:
            raise AttributeError('Record (' + self.style + ') has no attribute todict')
        else:
            return todict(self.content, **kwargs)
    
    @property
    def schema(self):
        """Returns the path to the .xsd file for the named record."""
        
        try: 
            schema = self.__r_module.schema
        except AttributeError:
            raise AttributeError('Record (' + self.style + ') has no attribute schema') 
        else:
            return schema()