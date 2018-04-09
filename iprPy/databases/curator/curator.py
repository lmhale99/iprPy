# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import shutil
import tarfile
from io import BytesIO

# ADD INFO
import mdcs

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from iprPy.tools import iaslist
from iprPy import Record

__all__ = ['initialize', 'iget_records', 'get_records', 'get_record',
           'add_record', 'update_record', 'delete_record', 'add_tar',
           'get_tar']

def initialize(host, user=None, pswd=None, cert=None):
    """
    Initializes a database of style curator by defining database_info.
    
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
    
    Returns
    -------
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
    """
    
    # database_info is an mdcs.MDCS object
    return mdcs.MDCS(host=host, user=user, pswd=pswd, cert=cert,
                     build_records=False)

def iget_records(database_info, name=None, style=None):
    """
    Iterates through matching records in the database.
    
    Parameters
    ----------
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
    name : str, optional
        The record name or id to limit the search by.
    style : str, optional
        The record style to limit the search by.
        
    Yields
    ------
    iprPy.Record
        Each record from the database matching the given parameters.
    """
    
    # Iterate through all files matching style, name values
    for s in iaslist(style):
        for n in iaslist(name):
            database_info.build_records(template=s, title=n)
            for i, row in database_info.records.iterrows():
                
                # Yield an iprPy.Record object
                style = database_info.get_template(row.schema).title
                name = row.title
                content = row.content.encode('utf-8')
                yield Record(style=style, name=name, content=content)
    
def get_records(database_info, name=None, style=None):
    """
    Produces a list of all matching records in the database.
    
    Parameters
    ----------
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
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
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
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
    Adds a new record to the database.  Will issue an error if a 
    matching record already exists in the database.
    
    Parameters
    ----------
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
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
    matching_records = get_records(database_info, name=record.name,
                                   style=record.style)
    if len(matching_records) > 0:
        raise ValueError('Record ' + record.name + ' already exists')
    
    # Upload record to database
    database_info.add_record(record.content, record.name, record.style,
                             refresh=False)
    
    return record
    
def update_record(database_info, record=None, style=None, name=None,
                  content=None):
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
    
    database_info.update_record(oldrecord.name, record.content, refresh=False)
    
    return record
    
def delete_record(database_info, record=None, name=None, style=None):
    """
    Permanently deletes a record from the database.  Will issue an error 
    if exactly one matching record is not found in the database.
    
    Parameters
    ----------
    database_info : mdcs.MDCS
        The MDCS class used for accessing the curator database.
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
    
    # Delete record
    database_info.delete_record(record.name, refresh=False)
    
def add_tar(database_info, record=None, name=None, style=None, root_dir=None):
    """
    Archives and stores a folder associated with a record.  Issues an
    error if exactly one matching record is not found in the database, or
    the associated record already has a tar archive. The record's name
    must match the name of the directory being archived.
    
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
    
    # Check if an archive already exists
    model = DM(record.content)
    #if len(model.finds('archive')) > 0:
    #    raise ValueError('Record already has an archive')
    
    # Make archive
    shutil.make_archive(record.name, 'gztar', root_dir=root_dir,
                        base_dir=record.name)
    
    # Upload archive
    tries = 0
    while tries < 2:
        try:
            url = database_info.add_file(record.name + '.tar.gz')
            break
        except:
            tries += 1
    if tries == 2:
        raise ValueError('Failed to upload archive 2 times')
    
    # Update corresponding record
    root_key = model.keys()[0]
    model[root_key]['archive'] = DM()
    model[root_key]['archive']['url'] = url
    
    update_record(database_info, name=record.name, style=record.style,
                  content=model.xml())
    
    # Remove local archive copy
    os.remove(record.name+'.tar.gz')

def get_tar(database_info, record=None, name=None, style=None, raw=False):
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
        record = get_record(database_info, name=name, style=style)
    
    # Issue a TypeError for competing kwargs
    elif style is not None or name is not None:
        raise TypeError('kwargs style and name cannot be given with kwarg record')
    
    # Verify that record exists
    else:
        record = get_record(database_info, name=record.name, style=record.style)
    
    # Extract url and download tar file
    model = DM(record.content)
    url = model.find('archive')['url']
    tardata = database_info.get_file(url)
    
    # Return content
    if raw is True:
        return tardata
    else:
        return tarfile.open(fileobj = BytesIO(tardata))