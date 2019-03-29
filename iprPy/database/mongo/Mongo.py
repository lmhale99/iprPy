# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import glob
import shutil
import tarfile
from collections import OrderedDict

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://api.mongodb.com/python/current/
from pymongo import MongoClient
from gridfs import GridFS
from bson.codec_options import CodecOptions

from DataModelDict import DataModelDict as DM

# iprPy imports
from ...tools import aslist, iaslist
from .. import Database
from ... import load_record
from ...record import loaded as record_styles

class Mongo(Database):
    
    def __init__(self, host, user=None, pswd=None):
        """
        Initializes a connection to a Mongo database.
        
        Parameters
        ----------
        host : str, tuple
            The mongo database name or tuple of (client, database).  If client is
            not given, will use default localhost.
        user : str or tuple of two str
            The username to use for accessing the database.  Alternatively, a
            tuple of (user, pswd).
        pswd : str, optional
            The password associated with user to use for accessing the database.
            This can either be the password as a str, or a str path to a file
            containing only the password. If not given, a prompt will ask for the
            password.
        """
        # Connect
        if isinstance(host, str):
            self.mongodb = MongoClient()[host]
        elif len(host) == 2:
            self.mongodb = MongoClient(host[0])[host[1]]
        self.mongofs = GridFS(self.mongodb)
        host = str(self.mongodb.client.address[0]) + ':' + str(self.mongodb.client.address[1]) + '.' + self.mongodb.name
        
        # Pass host to Database initializer
        Database.__init__(self, host)
    
    def get_records(self, name=None, style=None, query=None, return_df=False,
                    **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
        query : str, optional
            A query str for identifying records.  Not supported by this style.
        return_df : bool, optional
            
        Returns
        ------
        list of iprPy.Records
            All records from the database matching the given parameters.
        """
        codec_options = CodecOptions(document_class=DM)

        if style is None:
            style = list(record_styles.keys())
        else:
            style = aslist(style)

        # Handle query-based parameters
        if query is None:
            query = {}
            if name is not None:
                query['name'] = {}
                query['name']['$in'] = aslist(name)
        elif name is not None:
            raise ValueError('name and query cannot both be given')
        
        df = []
        records = []
        for s in style:
            collection = self.mongodb.get_collection(s, codec_options=codec_options)
            for entry in collection.find(query):
                
                # Load as Record object
                record = load_record(s, entry['name'], entry['content'])
                records.append(record)
                df.append(record.todict(full=False, flat=True))
                
        records = np.array(records)
        df = pd.DataFrame(df)

        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]

        if return_df:
            return list(records[df.index.tolist()]), df.reset_index()
        else:
            return list(records[df.index.tolist()])

    def get_records_df(self, name=None, style=None, query=None, full=True,
                       flat=False, **kwargs):
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
        """
        codec_options = CodecOptions(document_class=DM)
        
        if style is None:
            style = list(record_styles.keys())
        else:
            style = aslist(style)

        # Handle query-based parameters
        if query is None:
            query = {}
            if name is not None:
                query['name'] = {}
                query['name']['$in'] = aslist(name)
        elif name is not None:
            raise ValueError('name and query cannot both be given')
        
        df = []
        for s in style:
            collection = self.mongodb.get_collection(s, codec_options=codec_options)
            for entry in collection.find(query):
                    
                # Load as Record object
                record = load_record(s, entry['name'], entry['content'])
                df.append(record.todict(full=full, flat=flat))
                
        df = pd.DataFrame(df)
        
        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]
        
        return df

    def get_record(self, name=None, style=None, query=None, **kwargs):
        """
        Returns a single matching record from the database.
        
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
        ValueError
            If multiple or no matching records found.
        """
        
        # Get records
        record = self.get_records(name=name, style=style, query=None, **kwargs)
        
        # Verify that there is only one matching record
        if len(record) == 1:
            return record[0]
        elif len(record) == 0:
            raise ValueError('Cannot find matching record '+ name + ' (' +style + ')')
        else:
            raise ValueError('Multiple matching records found')    

    def add_record(self, record=None, style=None, name=None, content=None):
        """
        Adds a new record to the database.
        
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
        ValueError
            If style, name and/or content given with record, or a matching record
            already exists.
        """

        # Create Record object if not given
        if record is None:
            record = load_record(style, name, content)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None or content is not None:
            raise ValueError('kwargs style, name, and content cannot be given with kwarg record')

        # Verify that there isn't already a record with a matching name
        if len(self.get_records(name=record.name, style=record.style)) > 0:
            raise ValueError('Record ' + record.name + ' already exists')

        # Create meta mongo entry
        entry = OrderedDict()
        entry['name'] = record.name
        entry['content'] = record.content
        
        # Upload to mongodb
        self.mongodb[record.style].insert_one(entry)

        return record

    def update_record(self, record=None, style=None, name=None, content=None):
        """
        Replaces an existing record with a new record of matching name and
        style, but new content.
        
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
        TypeError
            If no new content is given.
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            if content is None:
                raise TypeError('no new content given')
            oldrecord = self.get_record(name=name, style=style)
            record = load_record(oldrecord.style, oldrecord.name, content)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Replace content in record object
        elif content is not None:
            oldrecord = record
            record = load_record(oldrecord.style, oldrecord.name, content)
            
        # Find oldrecord matching record
        else:
            oldrecord = self.get_record(name=record.name, style=record.style)
        
        # Delete oldrecord
        self.delete_record(record=oldrecord)
        
        # Add new record
        self.add_record(record=record)
        
        return record
    
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
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)

        # Build delete query
        query = {}
        query['name'] = record.name

        # Delete record 
        self.mongodb[record.style].delete_one(query)

    def add_tar(self, record=None, name=None, style=None, root_dir=None):
    
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)

        # Make archive
        shutil.make_archive(record.name, 'gztar', root_dir=root_dir,
                            base_dir=record.name)

        filename = record.name + '.tar.gz'
        with open(filename, 'rb') as f:
        
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    self.mongofs.put(f, recordstyle=record.style, recordname=record.name, databasename=self.mongodb.name)
                    break
                else:
                    tries += 1
            if tries == 2:
                raise ValueError('Failed to upload archive 2 times')

        # Remove local archive copy
        os.remove(filename)
        
    def get_tar(self, record=None, name=None, style=None, raw=False):
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)

        # Issue a TypeError for competing kwargs
        elif style is not None or name is not None:
            raise TypeError('kwargs style and name cannot be given with kwarg record')

        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)

        # Build query
        query = {}
        query['recordstyle'] = record.style
        query['recordname'] = record.name    
        query['databasename'] = self.mongodb.name
        
        # Get tar
        matches = list(self.mongofs.find(query))
        if len(matches) == 1:
            tar = matches[0]
        elif len(matches) == 0:
            raise ValueError('No tar found for the record')
        else:
            raise ValueError('Multiple tars found for the record')

        # Return content
        if raw is True:
            return tar.read()
        else:
            return tarfile.open(fileobj=tar)

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
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Build query
        query = {}
        query['recordstyle'] = record.style
        query['recordname'] = record.name    
        query['databasename'] = self.mongodb.name
        
        # Get tar
        matches = list(self.mongofs.find(query))
        if len(matches) == 1:
            tar = matches[0]
        elif len(matches) == 0:
            raise ValueError('No tar found for the record')
        else:
            raise ValueError('Multiple tars found for the record')

        # Delete tar
        self.mongofs.delete(tar._id)

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
        """
        
        # Delete the existing tar archive stored in the database
        self.delete_tar(record=record, name=name)
        
        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, root_dir=root_dir)