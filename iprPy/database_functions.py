from .databases import databases_dict

def database_styles():
    """Returns a list of the styles of the loaded databases."""
    return databases_dict.keys()
    
def database_fromdict(input_dict, database_key='database'):
    """Takes a dictionary from an input file and returns a Database object"""
    
    db = input_dict[database_key].split()
    db_type = db[0]
    db_name = ' '.join(db[1:])
    db_terms = {}
    for key in input_dict:
        if key[:9] == database_key + '_':
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
            initialize = self.__db_module.initialize
        except AttributeError:
            raise AttributeError('Database (' + style + ') has no attribute initialize')  
        else:
            self.__db_info = initialize(host, *args, **kwargs)
        
        #Set property values
        self.__style = style
        self.__host = host
    
    def __str__(self):
        return 'iprPy.Database (' + self.style + ') at ' + self.host 
    
    @property
    def style(self):
        return self.__style
        
    @property
    def host(self):
        return self.__host
    
    def iget_records(self, name=None, style=None):
        """Iterates through records matching given conditions"""
        try: 
            iget_records = self.__db_module.iget_records
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute iget_records')
        else:
            return iget_records(self.__db_info, name, style)

    def get_records(self, name=None, style=None):
        """Returns a list of records matching given conditions"""
        try: 
            get_records = self.__db_module.get_records
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute get_records')
        else:
            return get_records(self.__db_info, name, style)
    
    def get_record(self, name=None, style=None):
        """Returns a single record matching given conditions. Issues an error if none or multiple matches are found."""
        try: 
            get_record = self.__db_module.get_record
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute get_record')
        else:
            return get_record(self.__db_info, name, style)
    
    def add_record(self, record=None, name=None, style=None, content=None):
        """Adds a new record to the database"""
        try: 
            add_record = self.__db_module.add_record
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute add_record')
        else:
            return add_record(self.__db_info, record=record, name=name, style=style, content=content)
        
    def update_record(self, record=None, name=None, style=None, content=None):
        """Updates an existing record in the database"""
        try: 
            update_record = self.__db_module.update_record
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute update_record')
        else:
            return update_record(self.__db_info, record=record, name=name, style=style, content=content)
          
    def delete_record(self, record=None, name=None, style=None):
        """Deletes a record from the database"""
        try: 
            delete_record = self.__db_module.delete_record
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute delete_record')
        else:
            delete_record(self.__db_info, record=record, name=name, style=style)
        
    def get_tar(self, record=None, name=None, style=None):
        """Retrives a stored tar archive"""
        try: 
            get_tar = self.__db_module.get_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute get_tar')
        else:
            return get_tar(self.__db_info, record=record, name=name, style=style)
    
    def add_tar(self, record=None, name=None, style=None, root_dir=None):
        """Archives a folder as a tar file and saves to a record in the database"""
        try: 
            add_tar = self.__db_module.add_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute add_tar')
        else:
            add_tar(self.__db_info, record=record, name=name, style=style, root_dir=root_dir)
    
    def update_tar(self, record=None, name=None, style=None, root_dir=None):
        """Updates an existing tar file in the database"""
        try: 
            update_tar = self.__db_module.update_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute update_tar')
        else:
            return update_tar(self.__db_info, record=record, name=name, style=style, root_dir=root_dir)
    
    def delete_tar(self, record=None, name=None, style=None):
        """Deletes a tar file from the database"""
        try: 
            delete_tar = self.__db_module.delete_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style + ') has no attribute delete_tar')
        else:
            delete_tar(self.__db_info, record=record, name=name, style=style)