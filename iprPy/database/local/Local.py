# Standard Python libraries
from pathlib import Path
import shutil
import tarfile

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from ...tools import aslist, iaslist
from .. import Database
from ... import load_record
from ...record import loaded as record_styles

class Local(Database):
    
    def __init__(self, host):
        """
        Initializes a connection to a local database.
        
        Parameters
        ----------
        host : str
            The host name (local directory path) for the database.
        """
        # Get absolute path to host
        host = Path(host).resolve()
        
        # Make the path if needed
        if not host.is_dir():
            host.mkdir(parents=True)
        
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

        # Set default search parameters
        if style is None:
            style = list(record_styles.keys())
        else:
            style = aslist(style)
            for record_style in style:
                assert record_style in list(record_styles.keys()), f'unknown record style {record_style}'

        if query is not None:
            raise ValueError('query not supported by this style')
        
        df = []
        records = []
        # Iterate through all files matching style, name values
        for record_style in style:
            
            # Iterate over all names using glob
            if name is None:
                for record_file in Path(self.host, record_style).glob('*.xml'):
                    record_name = record_file.stem
                    
                    # Load as an iprPy.Record object
                    record = load_record(record_style, record_name, record_file)
                    records.append(record)
                    df.append(record.todict(full=False, flat=True))
            else:
                # Iterate over given names
                for record_name in aslist(name):
                    record_file = Path(self.host, record_style, record_name+'.xml')
                    if record_file.is_file():
                        
                        # Load as an iprPy.Record object
                        record = load_record(record_style, record_name, record_file)
                        records.append(record)
                        df.append(record.todict(full=False, flat=True))
        
        records = np.array(records)
        df = pd.DataFrame(df)
        
        if len(df) > 0:
            for key in kwargs:
                df = df[df[key].isin(aslist(kwargs[key]))]
        
        if return_df:
            return list(records[df.index.tolist()]), df.reset_index(drop=True)
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
        
       # Set default search parameters
        if style is None:
            style = list(record_styles.keys())
        else:
            style = aslist(style)
            for record_style in style:
                assert record_style in list(record_styles.keys()), f'unknown record style {record_style}'

        if query is not None:
            raise ValueError('query not supported by this style')
        
        df = []
       # Iterate through all files matching style, name values
        for record_style in style:
            
            # Iterate over all names using glob
            if name is None:
                for record_file in Path(self.host, record_style).glob('*.xml'):
                    record_name = record_file.stem

                    # Load as an iprPy.Record object
                    record = load_record(record_style, record_name, record_file)
                    df.append(record.todict(full=full, flat=flat))
            else:
                # Iterate over given names
                for record_name in aslist(name):
                    record_file = Path(self.host, record_style, record_name+'.xml')
                    if record_file.is_file():
                        
                        # Load as an iprPy.Record object
                        record = load_record(record_style, record_name, record_file)
                        df.append(record.todict(full=full, flat=flat))                    
                    
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
        record = self.get_records(name=name, style=style, query=None, **kwargs)
        
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
        
        # Make record style directory if needed
        style_dir = Path(self.host, record.style)
        if not style_dir.is_dir():
            style_dir.mkdir()
        
        # Save content to an .xml file
        xml_file = Path(style_dir, record.name+'.xml')
        with open(xml_file, 'w') as f:
            record.content.xml(fp=f)
        
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
        
        # Build path to record
        xml_path = Path(self.host, record.style, record.name+'.xml')
        
        # Delete record file
        xml_path.unlink()

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
        
        # Build path to record
        record_path = Path(self.host, record.style, record.name)
        tar_path = Path(self.host, record.style, f'{record.name}.tar.gz')
        
        # Check if an archive already exists
        if tar_path.is_file():
            raise ValueError('Record already has an archive')
        
        # Make archive
        if tar is None:
            if root_dir is None:
                root_dir = '.'
            target = Path(root_dir, record.name)

            tar = tarfile.open(tar_path, 'w:gz')
            tar.add(target, target.name)
            tar.close()
            
        elif root_dir is None:
            with open(tar_path, 'wb') as f:
                f.write(tar)
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
        
        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')
        
        # Verify that record exists
        else:
            record = self.get_record(name=record.name, style=record.style)
        
        # Build path to record
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')
        
        # Return content
        if raw is True:
            with open(tar_path, 'rb') as f:
                return f.read()
        else:
            return tarfile.open(tar_path)

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
        
        # Build path to tar file
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')
        
        # Delete record if it exists
        if tar_path.is_file():
            tar_path.unlink()

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
        self.delete_tar(record=record, name=name)
        
        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, tar=tar, root_dir=root_dir)