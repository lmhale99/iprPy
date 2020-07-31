# Standard Python libraries
from pathlib import Path
import shutil
import tarfile
from io import BytesIO

from cdcs import CDCS

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from ...tools import aslist, iaslist
from .. import Database
from ... import load_record

class CDCSDatabase(Database):
    
    def __init__(self, host, user=None, pswd=None, cert=None):
        """
        Initializes a database of style curator.
        
        Parameters
        ----------
        host : str
            The host name (url) for the database.
        user : str or tuple of two str
            The username to use for accessing the database.  Alternatively, a
            tuple of (user, pswd).
        pswd : str, optional
            The password associated with user to use for accessing the database.
            This can either be the password as a str, or a str path to a file
            containing only the password. If not given, a prompt will ask for the
            password.
        cert : str, optional
            The path to a certification file if needed for accessing the database.
        """
        
        # Pass parameters to cdcs object
        if Path(pswd).is_file():
            with open(pswd) as f:
                pswd = f.read().strip()
        self.cdcs = CDCS(host, username=user, password=pswd, certification=cert)
        
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
            
        Returns
        ------
        list of iprPy.Records
            All records from the database matching the given parameters.
        """
        
        records = []

        def build_records(series):
            return load_record(style=series.template_title, name=series.title, content=series.xml_content)

        for n in iaslist(name):
            data = self.cdcs.query(title=n, template=style, mongoquery=query)
            records.extend(data.apply(build_records, axis=1))

        if return_df or len(kwargs) > 0:
            df = []
            for record in records:
                df.append(record.todict(full=False, flat=True))
            df = pd.DataFrame(df)
        
            if len(df) > 0:
                for key in kwargs:
                    df = df[df[key].isin(aslist(kwargs[key]))]
            
            if return_df:
                return list(records[df.index.tolist()]), df.reset_index(drop=True)
            else:
                return list(records[df.index.tolist()])
        else:
            return records
    
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
        
        df = []
        def build_record_dicts(series, full, flat):
            return load_record(style=series.template_title, name=series.title,
                                     content=series.xml_content).todict(full=full, flat=flat)
        
        for n in iaslist(name):
            data = self.cdcs.query(title=n, template=style, mongoquery=query)
            df.extend(data.apply(build_record_dicts, args=[full, flat], axis=1))
        df = pd.DataFrame(df)
        
        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]
        
        return df.reset_index(drop=True)
    
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
        record = self.get_records(name=name, style=style, query=query, **kwargs)
        
        # Verify that there is only one matching record
        if len(record) == 1:
            return record[0]
        elif len(record) == 0:
            raise ValueError(f'Cannot find matching record {name} ({style})')
        else:
            raise ValueError('Multiple matching records found')
    
    def add_record(self, record=None, style=None, name=None, content=None):
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
            
        # Upload record to database
        self.cdcs.upload_record(template=record.style, content=record.content.xml(), title=record.name)
        
        return record
    
    def update_record(self, record=None, style=None, name=None, content=None):
        """
        Replaces an existing record with a new record of matching name and 
        style, but new content.  Will issue an error if exactly one 
        matching record is not found in the databse.
        
        Parameters
        ----------
        database_info : mdcs.MDCS
            The MDCS class used for accessing the curator database.
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
        
        # Use given record object
        else:
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')
            
            # Replace content in record object
            if content is not None:
                record = load_record(record.style, record.name, content)
        
        # Upload record to database
        self.cdcs.update_record(template=record.style, content=record.content.xml(), title=record.name)
        
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
        
        # Extract values from Record object if given
        if record is not None:
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')
            name = record.name
            style = record.style
         
        # Delete record
        self.cdcs.delete_record(template=style, title=name)
    
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
        
        # Get Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        else:
            # Issue a ValueError for competing kwargs
            if style is not None or name is not None:
                raise ValueError('kwargs style and name cannot be given with kwarg record')

            # Verify that record exists
            record = self.get_record(name=record.name, style=record.style)
        
        # Check if an archive already exists
        blobs = self.cdcs.get_blobs(filename=record.name)
        if len(blobs) > 0:
            raise ValueError('Record already has an archive')
        
        filename = Path(record.name + '.tar.gz')

        # Create directory archive and upload
        if tar is None: 
            
            # Make archive
            shutil.make_archive(record.name, 'gztar', root_dir=root_dir,
                                base_dir=record.name)
            
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    url = self.cdcs.upload_blob(filename.as_posix())
                    break
                else:
                    tries += 1
            if tries == 2:
                raise ValueError('Failed to upload archive 2 times')
            
            # Remove local archive copy
            filename.unlink()
        
        # Upload pre-existing tar object
        elif root_dir is None:
            # Upload archive
            tries = 0
            while tries < 2:
                if True:
                    url = self.cdcs.upload_blob(filename=filename, blobbytes=BytesIO(tar))
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
        database_info : mdcs.MDCS
            The MDCS class used for accessing the curator database.
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
        
        filename = Path(record.name + '.tar.gz')

        # Download tar file
        tardata = self.cdcs.get_blob_contents(filename=filename)
        
        # Return contents
        if raw is True:
            return tardata
        else:
            return tarfile.open(fileobj = BytesIO(tardata))
    
    def delete_tar(self, record=None, name=None, style=None):
        # Create Record object if not given
        if record is None:
            record = self.get_record(name=name, style=style)
        
        # Issue a TypeError for competing kwargs
        elif style is not None or name is not None:
            raise TypeError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        filename = Path(record.name + '.tar.gz')

        self.cdcs.delete_blob(filename=filename)

    def update_tar(self, record=None, name=None, style=None, tar=None, root_dir=None):
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
        
        self.delete_tar(record=record, name=name, style=style)
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)