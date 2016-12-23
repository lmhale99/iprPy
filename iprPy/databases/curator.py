import os
import shutil
import tarfile
import requests
from io import BytesIO

import mdcs 
from DataModelDict import DataModelDict as DM

from iprPy.tools import iaslist

def initialize(host=None, user=None, pswd=None, cert=None):
    """Initializes access to a mdcs database"""
    
    return mdcs.MDCS(host, user, pswd, cert, records_fetch=False)
    

def iget_records(database_info, record_type=None, key=None):
    """Iterates through matching records in the database"""    
    
    record_paths = []
    
    for rtype in iaslist(record_type):
        for k in iaslist(key):
            database_info.build_records(template=rtype, title=k)
            for i, row in database_info.records.iterrows():
                yield row.content.encode('utf-8')
    
def get_records(database_info, record_type=None, key=None):
    """Retrieves records from a database"""
    
    return [i for i in iget_records(database_info, record_type, key)]
    
def add_record(database_info, record_data, record_type, key):
    """Adds a new record to a database"""
    
    if len(get_records(database_info, key=key)) > 0:
        raise ValueError('Record ' + key + ' already exists')
        
    database_info.add_record(record_data, key, record_type, refresh=False)        
    
def update_record(database_info, record_data, key):
    """Updates an existing record in a database"""
    
    database_info.update_record(key, record_data, refresh=False)
    
def delete_record(database_info, key):
    """deletes an existing record in a database"""
    
    database_info.delete_record(key, refresh=False)
    
def add_archive(database_info, run_directory, key):
    """Archives calculation folder and saves to the database"""

    #Find record
    record = get_records(database_info, key=key)
    
    #If exactly one match is found, add archive with matching name
    if len(record) == 1:
        record = DM(record[0])
        
        #Check if an archive already exists
        assert len(record.finds('archive')) == 0, 'Record already has an archive'
        
        #Make archive
        shutil.make_archive(key, 'gztar', root_dir=run_directory, base_dir=key)
        
        #Upload archive
        root_key = record.keys()[0]
        record[root_key]['archive'] = DM()
        record[root_key]['archive']['url'] = database_info.add_file(key+'.tar.gz')
        update_record(database_info, record.xml(), key)
        
        #Remove local archive copy
        os.remove(key+'.tar.gz')

    elif len(record) == 0:
        raise ValueError('Record for ' + key + ' not found')
    else:
        raise ValueError('Multiple records for ' + key + ' found') 

def get_archive(database_info, key):
    """Retrives a stored calculation archive"""

    #Find record
    record = get_records(database_info, key=key)
    
    #If exactly one match is found, get archive from url
    if len(record) == 1:
        record = DM(record[0])
        
        url = record.find('archive')['url']
        
        return tarfile.open(fileobj = BytesIO(database_info.get_file(url)))    
    
    elif len(record) == 0:
        raise ValueError('Archive for ' + key + ' not found')
    
    else:
        raise ValueError('Multiple archives for ' + key + ' found') 