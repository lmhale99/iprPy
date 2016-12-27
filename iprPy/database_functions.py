from .databases import databases_dict

def database_styles():
    """Returns a list of the styles of the loaded databases."""
    return databases_dict.keys()
    
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

    def __init__(self, style, host, *args, **kwargs):
        """Initializes a connection to a database"""
        
        #Check if database style exists
        try:
            self.__db_module = databases_dict[style]
        except KeyError:
            raise KeyError('No database style ' + style + ' imported')
        
        #Check if database style has initialize method
        try: 
            self.__db_info = self.__db_module.initialize(host, *args, **kwargs)
        except AttributeError:
            raise AttributeError('Database style ' + style + ' has no attribute initialize')  
        
        self.__style = style
        self.__host = host
            
    @property
    def style(self):
        return self.__style
        
    @property
    def host(self):
        return self.__host
    
    def iget_records(self, name=None, style=None):
        """Iterates through records matching given conditions"""
        try: 
            return self.__db_module.iget_records(self.__db_info, name, style)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute iget_records')  

    def get_records(self, name=None, style=None):
        """Returns a list of records matching given conditions"""
        try: 
            return self.__db_module.get_records(self.__db_info, name, style)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute get_records')
    
    def get_record(self, name=None, style=None):
        """Returns a single record matching given conditions. Issues an error if none or multiple matches are found."""
        try: 
            return self.__db_module.get_record(self.__db_info, name, style)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute get_record')
    
    def add_record(self, record=None, name=None, style=None, content=None):
        """Adds a new record to the database"""
        try: 
            return self.__db_module.add_record(self.__db_info, record=record, name=name, style=style, content=content)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute add_record')
        
    def update_record(self, record=None, name=None, style=None, content=None):
        """Updates an existing record in the database"""
        try: 
            return self.__db_module.update_record(self.__db_info, record=record, name=name, style=style, content=content)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute update_record')
            
    def delete_record(self, record=None, name=None, style=None):
        """Deletes a record from the database"""
        try: 
            return self.__db_module.delete_record(self.__db_info, record=record, name=name, style=style)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute delete_record')
        
    def add_archive(self, record=None, name=None, style=None, root_dir=None):
        """Archives a folder and saves it to the database"""
        try: 
            return self.__db_module.add_archive(self.__db_info, record=record, name=name, style=style, root_dir=root_dir)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute add_archive')
        
    def get_archive(self, record=None, name=None, style=None):
        """Retrives a stored calculation archive"""
        try: 
            return self.__db_module.get_archive(self.__db_info, record=record, name=name, style=style)
        except AttributeError:
            raise AttributeError('Database style ' + self.__style + ' has no attribute get_archive')
        
