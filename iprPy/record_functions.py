from DataModelDict import DataModelDict as DM
from io import BytesIO

from .records import records_dict

#Utility functions
def record_names():
    """Returns a list of the names of the loaded calculations."""
    return records_dict.keys()

def get_record(record_type):
    """Returns record module if it exists"""
    try:
        return records_dict[record_type]
    except:
        raise KeyError('No record ' + record_type + ' imported')
        
#Method specific functions    
def record_todict(record_data, record_type=None, **kwargs):
    """Converts an xml record to a flat dictionary"""
    
    if record_type is None:
        record_type = DM(record_data).keys()[0]
    
    record = get_record(record_type)
    try: todict = record.todict
    except:
        raise AttributeError('Record ' + record_type + ' has no attribute todict') 
    
    return todict(record_data, **kwargs)
    
def record_schema(record_type):
    """Returns the path to the .xsd file for the named record."""
    
    record = get_record(record_type)
    try: schema = record.schema
    except:
        raise AttributeError('Record ' + record_type + ' has no attribute schema') 
    
    return schema()

    
    
    
