# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from .databases import databases_dict

__all__ = ['database_styles', 'database_fromdict', 'Database']

def database_styles():
    """
    Returns
    -------
    list of str
        All database styles successfully loaded.
    """
    return databases_dict.keys()
    
def database_fromdict(input_dict, database_key='database'):
    """
    Initializes a Database object based on 'database_*' terms contained within
    a dictionary.
    
    Parameters
    ----------
    input_dict : dict
        Dictionary of input parameter terms including 'database' and any other
        necessary 'database_*' keys to fully initialize a Database object.
    database_key : str, optional
        Defines the base string for identifying the database keys.  Useful if
        multiple database definitions are needed.  (Default is 'database').
    
    Returns
    -------
    iprPy.Database
        Database object initialized from input_dict database keys.
    """
    # Split 'database' into style and name 
    db = input_dict[database_key].split()
    db_style = db[0]
    db_name = db.replace(db_style, '', 1).strip()
    
    # Extract all 'database_*' terms
    db_terms = {}
    for key in input_dict:
        if key[:9] == database_key + '_':
            db_terms[key[9:]] = input_dict[key]

    return Database(db_style, db_name, **db_terms)
        
class Database(object):
    """
    Class for handling different database styles in the same fashion.  The
    class defines the common methods and attributes, which are then uniquely
    implemented for each style.  The available styles are loaded from the
    iprPy.databases submodule.
    """

    def __init__(self, style, host, *args, **kwargs):
        """
        Initializes a connection to a database.
        
        Parameters
        ----------
        style : str
            The database style.
        host : str
            The host name (path, url, etc.) for the database.
        *args, **kwargs : optional
            Any additional terms necessary to gain access to the host
            database.  See the specific styles for allowed terms.
            
        Raises
        ------
        KeyError
            If the database style is not available.
        AttributeError
            If initialize is not defined for database style.
        """
        
        #Check if database style exists
        try:
            self.__db_module = databases_dict[style]
        except KeyError:
            raise KeyError('No database style ' + style + ' imported')
        
        #Check if database style has initialize method
        try: 
            initialize = self.__db_module.initialize
        except AttributeError:
            raise AttributeError('Database (' + style 
                                 + ') has no attribute initialize')
        else:
            self.__db_info = initialize(host, *args, **kwargs)
        
        #Set property values
        self.__style = style
        self.__host = host
    
    def __str__(self):
        """
        Returns
        -------
        str
            The string representation of the database: 
            iprPy.Database (<style>) at <host>.
        """
        return 'iprPy.Database (' + self.style + ') at ' + self.host
    
    @property
    def style(self):
        """str: The database's style."""
        return self.__style
        
    @property
    def host(self):
        """str: The database's host."""
        return self.__host
    
    def iget_records(self, name=None, style=None):
        """
        Iterates through matching records in the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
            
        Yields
        ------
        iprPy.Record
            Each record from the database matching the given parameters.
        
        Raises
        ------
        AttributeError
            If iget_records is not defined for database style.
        """
        try: 
            iget_records = self.__db_module.iget_records
        except AttributeError:
            raise AttributeError('Database (' + self.style 
                                 + ') has no attribute iget_records')
        else:
            return iget_records(self.__db_info, name, style)

    def get_records(self, name=None, style=None):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
            
        Returns
        ------
        list of iprPy.Records
            All records from the database matching the given parameters.
        
        Raises
        ------
        AttributeError
            If get_records is not defined for database style.
        """
        try: 
            get_records = self.__db_module.get_records
        except AttributeError:
            raise AttributeError('Database (' + self.style 
                                 + ') has no attribute get_records')
        else:
            return get_records(self.__db_info, name, style)
    
    def get_record(self, name=None, style=None):
        """
        Returns a single matching record from the database.  Issues an error
        if multiple or no matching records are found.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
            
        Returns
        ------
        iprPy.Record
            The single record from the database matching the given parameters.
        
        Raises
        ------
        AttributeError
            If get_record is not defined for database style.
        """
        try: 
            get_record = self.__db_module.get_record
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute get_record')
        else:
            return get_record(self.__db_info, name, style)
    
    def get_records_df(self, name=None, style=None, full=True, flat=False):
        """
        Produces a pandas.DataFrame of all matching records in the database.
        
        Parameters
        ----------
        style : str
            The record style to collect records of.
        full : bool, optional
            Flag used by the calculation records.  A True value will include
            terms for both the calculation's input and results, while a value
            of False will only include input terms (Default is True).
        flat : bool, optional
            Flag affecting the format of the dictionary terms.  If True, the
            dictionary terms are limited to having only str, int, and float
            values, which is useful for comparisons.  If False, the term
            values can be of any data type, which is convenient for analysis.
            (Default is False).
        
        Returns
        ------
        pandas.DataFrame
            All records from the database of the given record style.
        """
        
        df = []
        for record in self.iget_records(name=name, style=style):
            df.append(record.todict(full=full, flat=flat))
        return pd.DataFrame(df)
    
    def add_record(self, record=None, name=None, style=None, content=None):
        """
        Adds a new record to the database.  Will issue an error if a
        matching record already exists in the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The new record to add to the database.  If not given, then name,
            style and content are required.
        name : str, optional
            The name to assign to the new record.  Required if record is not
            given.
        style : str, optional
            The record style for the new record.  Required if record is not
            given.
        content : str, optional
            The xml content of the new record.  Required if record is not
            given.
            
        Returns
        ------
        iprPy.Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        AttributeError
            If add_record is not defined for database style.
        """
        try: 
            add_record = self.__db_module.add_record
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute add_record')
        else:
            return add_record(self.__db_info, record=record, name=name,
                              style=style, content=content)
        
    def update_record(self, record=None, name=None, style=None, content=None):
        """
        Replaces an existing record with a new record of matching name and
        style, but new content.  Will issue an error if exactly one
        matching record is not found in the databse.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record with new content to update in the database.  If not
            given, content is required along with name and/or style to
            uniquely define a record to update.
        name : str, optional
            The name to uniquely identify the record to update.
        style : str, optional
            The style of the record to update.
        content : str, optional
            The new xml content to use for the record.  Required if record is
            not given.
            
        Returns
        ------
        iprPy.Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        AttributeError
            If update_record is not defined for database style.
        """
        try: 
            update_record = self.__db_module.update_record
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute update_record')
        else:
            return update_record(self.__db_info, record=record, name=name,
                                 style=style, content=content)
          
    def delete_record(self, record=None, name=None, style=None):
        """
        Permanently deletes a record from the database.  Will issue an error
        if exactly one matching record is not found in the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to delete from the database.  If not given, name and/or
            style are needed to uniquely define the record to delete.
        name : str, optional
            The name of the record to delete.
        style : str, optional
            The style of the record to delete.
        
        Raises
        ------
        AttributeError
            If delete_record is not defined for database style.
        """
        try: 
            delete_record = self.__db_module.delete_record
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute delete_record')
        else:
            delete_record(self.__db_info, record=record, name=name,
                          style=style)
        
    def get_tar(self, record=None, name=None, style=None, raw=False):
        """
        Retrives the tar archive associated with a record in the database.
        Issues an error if exactly one matching record is not found in the
        database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to retrive the associated tar archive for.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        raw : bool, optional
            If True, return the archive as raw binary content. If
            False, return as an open tarfile. (Default is False)
            
        Returns
        -------
        tarfile or str
            The tar archive as an open tarfile if raw=False, or as a binary
            str if raw=True.
        
        Raises
        ------
        AttributeError
            If get_tar is not defined for database style.
        """
        try: 
            get_tar = self.__db_module.get_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute get_tar')
        else:
            return get_tar(self.__db_info, record=record, name=name,
                           style=style, raw=raw)
    
    def add_tar(self, record=None, name=None, style=None, root_dir=None):
        """
        Archives and stores a folder associated with a record.  Issues an
        error if exactly one matching record is not found in the database, or
        the associated record already has a tar archive. The record's name
        must match the name of the directory being archived.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to associate the tar archive with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)
        
        Raises
        ------
        AttributeError
            If add_tar is not defined for database style.
        """
        try: 
            add_tar = self.__db_module.add_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute add_tar')
        else:
            add_tar(self.__db_info, record=record, name=name, style=style,
                    root_dir=root_dir)
    
    def update_tar(self, record=None, name=None, style=None, root_dir=None):
        """
        Replaces an existing tar archive for a record with a new one.  Issues
        an error if exactly one matching record is not found in the database.
        The record's name must match the name of the directory being archived.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record to associate the tar archive with.  If not given, then 
            name and/or style necessary to uniquely identify the record are 
            needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.
        
        Raises
        ------
        AttributeError
            If update_tar is not defined for database style.
        """
        try: 
            update_tar = self.__db_module.update_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute update_tar')
        else:
            return update_tar(self.__db_info, record=record, name=name,
                              style=style, root_dir=root_dir)
    
    def delete_tar(self, record=None, name=None, style=None):
        """
        Deletes a tar file from the database.  Issues an error if exactly one
        matching record is not found in the database.
        
        Parameters
        ----------
        record : iprPy.Record, optional
            The record associated with the tar archive to delete.  If not
            given, then name and/or style necessary to uniquely identify
            the record are needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        
        Raises
        ------
        AttributeError
            If delete_tar is not defined for database style.
        """
        try: 
            delete_tar = self.__db_module.delete_tar
        except AttributeError:
            raise AttributeError('Database (' + self.style
                                 + ') has no attribute delete_tar')
        else:
            delete_tar(self.__db_info, record=record, name=name, style=style)