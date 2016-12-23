from .databases import databases_dict

#Utility functions
def database_names():
    """Returns a list of the names of the loaded databases."""
    return databases_dict.keys()
    
def get_database(name):
    """Returns database module if it exists"""
    try:
        return databases_dict[name]
    except:
        raise KeyError('No database ' + name + ' imported')

def database_fromdict(input_dict):
    """Takes a dictionary from an input file and returns a Database object"""
    
    db = input_dict['database'].split()
    db_type = db[0]
    db_name = ' '.join(db[1:])
    db_terms = {}
    for key in input_dict:
        if key[:9] == 'database_':
            db_terms[key[9:]] = input_dict[key]

    return Database(db_type, db_name, **db_terms)   
        
class Database(object):
    """Class for handling different databases in the same fashion"""

    def __init__(self, style, *args, **kwargs):
        """Initializes a connection to a database"""
        
        self.__style = style
        self.__db_module = get_database(style)
        
        try: 
            test = self.__db_module.initialize
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute initialize')  
        else:
            self.__db_info = self.__db_module.initialize(*args, **kwargs)
    
    def iget_records(self, record_type=None, key=None):
        """Iterates through records matching given conditions"""
        try: 
            test = self.__db_module.iget_records
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute iget_records')  
        else:
            return self.__db_module.iget_records(self.__db_info, record_type, key)

    def get_records(self, record_type=None, key=None):
        """Returns a list of records matching given conditions"""
        try: 
            test = self.__db_module.get_records
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute get_records')
        else:
            return self.__db_module.get_records(self.__db_info, record_type, key)
    
    def get_record(self, record_type=None, key=None):
        """Returns a single record matching given conditions. Issues an error if none or multiple matches are found."""
        
        record = self.get_records(record_type, key)
        if len(record) == 1:
            return record[0]
        elif len(record) == 0:
            raise ValueError('Cannot find matching record')
        else:
            raise ValueError('Multiple matching records found')
    
    def add_record(self, record_data, record_type, key):
        """Adds a new record to the database"""
        try: 
            test = self.__db_module.add_record
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute add_record')
        else:
            return self.__db_module.add_record(self.__db_info, record_data, record_type, key)
        
    def update_record(self, record_data, key):
        """Updates an existing record in the database"""
        try: 
            test = self.__db_module.update_record
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute update_record')
        else:
            return self.__db_module.update_record(self.__db_info, record_data, key)
            
    def delete_record(self, key=None):
        """Deletes a record from the database"""
        try: 
            test = self.__db_module.delete_record
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute delete_record')
        else:        
            return self.__db_module.delete_record(self.__db_info, key)
        
    def add_archive(self, run_directory, key):
        """Archives a folder and saves it to the database"""
        try: 
            test = self.__db_module.add_archive
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute add_archive')
        else:
            return self.__db_module.add_archive(self.__db_info, run_directory, key)

        
    def get_archive(self, key):
        """Retrives a stored calculation archive"""
        try: 
            test = self.__db_module.get_archive
        except:
            raise AttributeError('Database style ' + self.__style + ' has no attribute get_archive')
        else:
            return self.__db_module.get_archive(self.__db_info, key)
