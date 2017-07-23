from __future__ import division, absolute_import, print_function

__all__ = ['initialize', 'iget_records', 'get_records', 'get_record',
           'add_record', 'update_record', 'delete_record', 'add_tar',
           'get_tar', 'delete_tar', 'update_tar']

import os
import glob
import shutil
import tarfile

from iprPy.tools import iaslist
from iprPy import Record

def initialize(host):
    """
    Initializes a database of style local by defining database_info.
    
    Parameters
    ----------
    host : str
        The host name (local directory path) for the database.
    
    Returns
    -------
    database_info : str
        The absolute directory path to the database host.
    """
    
    # database_info is simply a local directory path
    database_info = os.path.abspath(host)
    
    # Make the directory path if needed
    if not os.path.isdir(database_info):
        os.makedirs(database_info)
        
    return database_info
    
def iget_records(database_info, name=None, style=None):
    """
    Iterates through matching records in the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
    name : str, optional
        The record name or id to limit the search by.
    style : str, optional
        The record style to limit the search by.
        
    Yields
    ------
    iprPy.Record
        Each record from the database matching the given parameters.
    """
    
    # Set default search parameters
    if style is None: style = ['*']
    if name is None: name = ['*']
    
    # Iterate through all files matching style, name, ext values
    for s in iaslist(style):
        for n in iaslist(name):
            for ext in iaslist(['.xml']):
                for rfile in glob.iglob(os.path.join(database_info, s, n+ext)):
                    rstyle = os.path.basename(os.path.dirname(rfile))
                    rname = os.path.splitext(os.path.basename(rfile))[0]
                    # Open record file and yield an iprPy.Record object
                    with open(rfile) as f:
                        yield Record(rstyle, rname, f.read())
    
def get_records(database_info, name=None, style=None):
    """
    Produces a list of all matching records in the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
    name : str, optional
        The record name or id to limit the search by.
    style : str, optional
        The record style to limit the search by.
        
    Returns
    ------
    list of iprPy.Records
        All records from the database matching the given parameters.
    """
    
    # Transform iterator into list
    return [i for i in iget_records(database_info, name=name, style=style)]

def get_record(database_info, name=None, style=None):
    """
    Returns a single matching record from the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
    record = get_records(database_info, name=name, style=style)
    
    # Verify that there is only one matching record
    if len(record) == 1:
        return record[0]
    elif len(record) == 0:
        raise ValueError('Cannot find matching record')
    else:
        raise ValueError('Multiple matching records found')
    
def add_record(database_info, record=None, style=None, name=None,
               content=None):
    """
    Adds a new record to the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
        record = Record(style, name, content)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None or content is not None:
        raise ValueError('kwargs style, name, and content cannot be given with kwarg record')
    
    # Verify that there isn't already a record with a matching name
    if len(get_records(database_info, name=record.name)) > 0:
        raise ValueError('Record ' + record.name + ' already exists')
    
    # Make record style directory if needed
    if not os.path.isdir(os.path.join(database_info, record.style)):
        os.mkdir(os.path.join(database_info, record.style))
    
    # Save content to an .xml file
    xml_file = os.path.join(database_info, record.style, record.name+'.xml')
    with open(xml_file, 'w') as f:
        f.write(record.content)
        
    return record
       
def update_record(database_info, record=None, style=None, name=None,
                  content=None):
    """
    Replaces an existing record with a new record of matching name and
    style, but new content.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
        oldrecord = get_record(database_info, name=name, style=style)
        record = Record(oldrecord.style, oldrecord.name, content)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None:
        raise ValueError('kwargs style and name cannot be given with kwarg record')
    
    # Replace content in record object
    elif content is not None:
        oldrecord = record
        record = Record(oldrecord.style, oldrecord.name, content)
        
    # Find oldrecord matching record
    else:
        oldrecord = get_record(database_info, name=record.name,
                               style=record.style)
    
    # Delete oldrecord
    delete_record(database_info, record=oldrecord)

    # Add new record
    add_record(database_info, record=record)
    
    return record
    
def delete_record(database_info, record=None, name=None, style=None):
    """
    Permanently deletes a record from the database.  Will issue an error 
    if exactly one matching record is not found in the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
        record = get_record(database_info, name=name, style=style)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None:
        raise ValueError('kwargs style and name cannot be given with kwarg record')
    
    # Verify that record exists
    else:
        record = get_record(database_info, name=record.name,
                            style=record.style)
    
    # Build path to record
    record_path = os.path.join(database_info, record.style, record.name)

    # Delete record file
    os.remove(record_path+'.xml')
        
def add_tar(database_info, record=None, name=None, style=None, root_dir=None):
    """
    Archives and stores a folder associated with a record.  Issues an
    error if exactly one matching record is not found in the database, or
    the associated record already has a tar archive. The record's name
    must match the name of the directory being archived.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
    ValueError
        If style and/or name content given with record or the record already
        has an archive.
    """

    # Create Record object if not given
    if record is None:
        record = get_record(database_info, name=name, style=style)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None:
        raise ValueError('kwargs style and name cannot be given with kwarg record')
    
    # Verify that record exists
    else:
        record = get_record(database_info, name=record.name,
                            style=record.style)
        
    # Build path to record
    record_path = os.path.join(database_info, record.style, record.name)

    # Check if an archive already exists
    if os.path.isfile(record_path+'.tar.gz'):
        raise ValueError('Record already has an archive')
        
    # Make archive
    shutil.make_archive(record_path, 'gztar', root_dir=root_dir,
                        base_dir=record.name)

def get_tar(database_info, record=None, name=None, style=None, raw=False):
    """
    Retrives the tar archive associated with a record in the database.
    Issues an error if exactly one matching record is not found in the 
    database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
        record = get_record(database_info, name=name, style=style)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None:
        raise ValueError('kwargs style and name cannot be given with kwarg record')
    
    # Verify that record exists
    else:
        record = get_record(database_info, name=record.name,
                            style=record.style)
    
    # Build path to record
    record_path = os.path.join(database_info, record.style, record.name)
    
    # Return content
    if raw is True:
        with open(record_path, 'rb') as f:
            return f.read()
    else:
        return tarfile.open(record_path+'.tar.gz')
    
def delete_tar(database_info, record=None, name=None, style=None):
    """
    Deletes a tar file from the database.  Issues an error if exactly one
    matching record is not found in the database.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
        record = get_record(database_info, name=name, style=style)
    
    # Issue a ValueError for competing kwargs
    elif style is not None or name is not None:
        raise ValueError('kwargs style and name cannot be given with kwarg record')
    
    # Verify that record exists
    else:
        record = get_record(database_info, name=record.name, style=record.style)
    
    # Build path to tar file
    record_path = os.path.join(database_info, record.style, record.name)
    
    # Delete record if it exists
    if os.path.isfile(record_path+'.tar.gz'):
        os.remove(record_path+'.tar.gz')
        
def update_tar(database_info, record=None, name=None, style=None,
               root_dir=None):
    """
    Replaces an existing tar archive for a record with a new one.  Issues
    an error if exactly one matching record is not found in the database.
    The record's name must match the name of the directory being archived.
    
    Parameters
    ----------
    database_info : str
        The absolute directory path to the database host.
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
    delete_tar(database_info, record=record, name=name)
    
    # Add the new tar archive
    add_tar(database_info, record=record, name=name, style=style,
            root_dir=root_dir)