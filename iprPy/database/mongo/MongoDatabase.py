# coding: utf-8
# Standard Python libraries
from pathlib import Path
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

from DataModelDict import DataModelDict as DM

# iprPy imports
from ...tools import aslist, iaslist
from .. import Database
from ... import load_record
from ...record import loaded as record_styles

class MongoDatabase(Database):
    
    def __init__(self, host='localhost', port=27017, database='iprPy', **kwargs):
        """
        Initializes a connection to a Mongo database.
        
        Parameters
        ----------
        host : str
            The mongo host to connect to.  Default value is 'localhost'.
        port : int
            Then port to use in connecting to the mongo host.  Default value
            is 27017.
        database : str
            The name of the database in the mongo host to interact with.
            Default value is 'iprPy'
        **kwargs : dict, optional
            Any extra keyword arguments needed to initialize a
            pymongo.MongoClient object.
        """
        
        # Connect to underlying class
        self.__mongodb = MongoClient(host=host, port=port, document_class=DM, **kwargs)[database]
        
        # Define class host using client's host, port and database name
        host = self.mongodb.client.address[0]
        port =self.mongodb.client.address[1]
        database = self.mongodb.name
        host = f'{host}:{port}.{database}'
        
        # Pass host to Database initializer
        Database.__init__(self, host)
    
    @property
    def mongodb(self):
        """pymongo.Database : The underlying database API object."""
        return self.__mongodb
    
    def build_query(self, style, name=None, **kwargs):
        """
        Constructs a mongo query based on the expected paths associated with
        certain keyword parameters.  The optional parameters below is the list
        of recognized keywords.
        
        NOTE: The constructed query assumes that the record follows the
        same convention of the majority of iprPy calculation records.  If the
        expected path is not in the record then any resulting mongo queries
        will fail.
        
        Parameters
        ----------
        style : str
            The record style.
        name : str or list, optional
            One or more record names to limit by.
        family : str or list, optional
            One or more system-info families to limit by.
        potential_LAMMPS_id : str or list, optional
            One or more LAMMPS potential implementation ids.
        potential_LAMMPS_key : str or list, optional
            One or more LAMMPS potential implementation keys.
        potential_id : str or list, optional
            One or more potential model ids.
        potential_key : str or list, optional
            One or more potential model keys.
        status : str, optional
            The calculation's status: 'finished', 'not calculated' or 'error'.
            Lists of status not (yet) supported.
            
        Returns
        -------
        query : dict
            The Mongo query as composed as a dict that pymongo can interpret.
        kwargs : dict
            Any remaining kwargs that were not recognized as having a known
            common record path.
        
        """
        root = style.replace('_', '-')
        
        query = {}

        # pop known kwargs and convert to query path
        if name is not None:
            query['name'] = {'$in': aslist(name)}
        if 'family' in kwargs:
            query[f'content.{root}.system-info.family'] = {'$in': aslist(kwargs.pop('family'))}
        if 'potential_LAMMPS_id' in kwargs:
            query[f'content.{root}.potential-LAMMPS.id'] = {'$in': aslist(kwargs.pop('potential_LAMMPS_id'))}
        if 'potential_LAMMPS_key' in kwargs:
            query[f'content.{root}.potential-LAMMPS.key'] = {'$in': aslist(kwargs.pop('potential_LAMMPS_key'))}
        if 'potential_id' in kwargs:
            query[f'content.{root}.potential-LAMMPS.potential.id'] = {'$in': aslist(kwargs.pop('potential_id'))}
        if 'potential_key' in kwargs:
            query[f'content.{root}.potential-LAMMPS.potential.key'] = {'$in': aslist(kwargs.pop('potential_key'))}
            
        if 'status' in kwargs:
            status = kwargs.pop('status')
            assert isinstance(status, str), 'lists of status not yet supported'
            if status == 'finished':
                query[f'content.{root}.status'] = {'$exists': False}
            else:
                query[f'content.{root}.status'] = status

        return query, kwargs
    
    def get_records(self, name=None, style=None, query=None, return_df=False,
                    fast=False, **kwargs):
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
        query : dict, optional
            A Mongo-style query to use for limiting the search.
        return_df : bool, optional
            Indicates if the corresponding pandas DataFrame for the records
            is to be also returned.  Default value is False.
        fast : bool, optional
            If True, the given kwargs will be passed through build_query to
            construct a mongo query based on expected paths for parameters.
            If True, then exactly one style value is required and query cannot
            be given.  Default value is False.
        **kwargs : any, optional
            Any extra keyword parameters will be used to parse records further
            based on record.todict() key-values.
            
        Returns
        ------
        numpy.NDArray of iprPy.Records
            All records from the database matching the given parameters.
        pandas.DataFrame
            The corresponding DataFrame for the records.  Returned if 
            return_df is True.
        """
        # Build query if fast is True
        if fast is True:
            if not isinstance(style, str):
                raise TypeError('Exactly one style is required if fast is True')
            if query is not None:
                raise ValueError('query cannot be given if fast is True')
            query, kwargs = self.build_query(style, name=name, **kwargs)
            style = aslist(style)
        
        # Build query if fast is False
        else:
            if style is None:
                style = list(record_styles.keys())
            else:
                style = aslist(style)

            # Handle query-based parameters
            if query is None:
                query = {}
                if name is not None:
                    query['name'] = {'$in': aslist(name)}
            elif name is not None:
                raise ValueError('name and query cannot both be given')
        
        # Query the collection to construct records and df
        df = []
        records = []
        for s in style:
            collection = self.mongodb[s]
            for entry in collection.find(query):
                
                # Load as Record object
                record = load_record(s, entry['name'], entry['content'])
                records.append(record)
                df.append(record.todict(full=False, flat=True))
        records = np.array(records)
        df = pd.DataFrame(df)

        # Further filter records using kwargs
        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]

        # Return records (and df)
        if return_df:
            return records[df.index.tolist()], df.reset_index(drop=True)
        else:
            return records[df.index.tolist()]

    def get_records_df(self, name=None, style=None, query=None, full=True,
                       flat=False, fast=False, **kwargs):
        """
        Produces a pandas.Dataframe of all matching records in the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
        query : dict, optional
            A Mongo-style query to use for limiting the search.
        full : bool, optional
            Indicates if the entries in the dataframe contain both input and
            results data (True) or only input data (False).  Default value is
            True.
        flat : bool, optional
            Indicates if the dataframe elements are to be flattened to simple
            terms (True) or left as complex objects (False).  Some values may
            be excluded if flat is True.  Default value is False.
        fast : bool, optional
            If True, the given kwargs will be passed through build_query to
            construct a mongo query based on expected paths for parameters.
            If True, then exactly one style value is required and query cannot
            be given.  Default value is False.
        **kwargs : any, optional
            Any extra keyword parameters will be used to parse records further
            based on record.todict() key-values.
            
        Returns
        ------
        list of iprPy.Records
            All records from the database matching the given parameters.
        """
        # Build query if fast is True
        if fast is True:
            if not isinstance(style, str):
                raise TypeError('Exactly one style is required if fast is True')
            if query is not None:
                raise ValueError('query cannot be given if fast is True')
            query, kwargs = self.build_query(style, name=name, **kwargs)
            style = aslist(style)
        
        # Build query if fast is False
        else:
            if style is None:
                style = list(record_styles.keys())
            else:
                style = aslist(style)

            # Handle query-based parameters
            if query is None:
                query = {}
                if name is not None:
                    query['name'] = {'$in': aslist(name)}
            elif name is not None:
                raise ValueError('name and query cannot both be given')
        
        # Query the collection to construct df
        df = []
        for s in style:
            collection = self.mongodb[s]
            for entry in collection.find(query):
                    
                # Load as Record object
                record = load_record(s, entry['name'], entry['content'])
                df.append(record.todict(full=full, flat=flat))
        df = pd.DataFrame(df)
        
        # Further filter records using kwargs
        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]
        
        # Return df
        return df.reset_index(drop=True)
    
    def get_record(self, name=None, style=None, query=None, fast=False,
                   **kwargs):
        """
        Retrieves a single matching record from the database.
        
        Parameters
        ----------
        name : str, optional
            The record name or id to limit the search by.
        style : str, optional
            The record style to limit the search by.
        query : dict, optional
            A Mongo-style query to use for limiting the search.
        fast : bool, optional
            If True, the given kwargs will be passed through build_query to
            construct a mongo query based on expected paths for parameters.
            If True, then exactly one style value is required and query cannot
            be given.  Default value is False.
        **kwargs : any, optional
            Any extra keyword parameters will be used to parse records further
            based on record.todict() key-values.
            
        Returns
        ------
        iprPy.Record
            The record from the database matching the given parameters.
        
        Raises
        ------
        ValueError
            If multiple or no matching records found.
        """
        
        # Get records
        record = self.get_records(name=name, style=style, query=query,
                                  fast=fast, **kwargs)
        
        # Verify that there is only one matching record
        if len(record) == 1:
            return record[0]
        elif len(record) == 0:
            raise ValueError(f'Cannot find matching record {name} ({style})')
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
            raise ValueError(f'Record {record.name} already exists')

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

    def add_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
        """
        Archives and stores a folder associated with a record.  Issues an
        error if exactly one matching record is not found in the database, or
        the associated record already has a tar archive.
        
        Parameters
        ----------
        database_info : mdcs.MDCS
            The MDCS class used for accessing the curator database.
        record : iprPy.Record, optional
            The record to associate the tar archive with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        name : str, optional
            .The name to use in uniquely identifying the record.
        style : str, optional
            .The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record or the record already
            has an archive.
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
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Check if an archive already exists
        if mongofs.exists({"recordname": record.name}):
            raise ValueError('Record already has an archive')
        
        if tar is None:
            if root_dir is None:
                root_dir = Path.cwd()
                
            # Make archive
            basename = Path(root_dir, record.name)
            filename = Path(root_dir, record.name + '.tar.gz')
            shutil.make_archive(basename, 'gztar', root_dir=root_dir,
                                base_dir=record.name)
        
            # Upload archive
            with open(filename, 'rb') as f:
                tries = 0
                while tries < 2:
                    if True:
                        mongofs.put(f, recordname=record.name)
                        break
                    else:
                        tries += 1
                if tries == 2:
                    raise ValueError('Failed to upload archive 2 times')
        
            # Remove local archive copy
            filename.unlink()
            
        elif root_dir is None:
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    mongofs.put(tar, recordname=record.name)
                    break
                else:
                    tries += 1
            if tries == 2:
                raise ValueError('Failed to upload archive 2 times')
        else:
            raise ValueError('tar and root_dir cannot both be given')
        
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
            The tar archive as an open tarfile if raw=False, or as a binary str if
            raw=True.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """
        
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a TypeError for competing kwargs
        elif style is not None or name is not None:
            raise TypeError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Build query
        query = {}
        query['recordname'] = record.name
        
        # Get tar
        matches = list(mongofs.find(query))
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
        
        # Define mongofs
        mongofs = GridFS(self.mongodb, collection=record.style)
        
        # Build query
        query = {}
        query['recordname'] = record.name
        
        # Get tar
        matches = list(mongofs.find(query))
        if len(matches) == 1:
            tar = matches[0]
        elif len(matches) == 0:
            raise ValueError('No tar found for the record')
        else:
            raise ValueError('Multiple tars found for the record')
        
        # Delete tar
        mongofs.delete(tar._id)
    
    def update_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
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
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        """
        
        # Delete the existing tar archive stored in the database
        self.delete_tar(record=record, name=name, style=style)
        
        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)