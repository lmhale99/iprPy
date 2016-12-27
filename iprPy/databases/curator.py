import os
import shutil
import tarfile
from io import BytesIO

import mdcs 
from DataModelDict import DataModelDict as DM

from iprPy.tools import iaslist
from iprPy import Record

def initialize(host, user=None, pswd=None, cert=None):
    """Initializes access to a mdcs database"""
    
    #database_info is an mdcs.MDCS object
    return mdcs.MDCS(host=host, user=user, pswd=pswd, cert=cert, build_records=False)

def iget_records(database_info, name=None, style=None):
    """Iterates through matching records in the database"""    
    
    #iterate through all files matching style, name values
    for s in iaslist(style):
        for n in iaslist(name):
            database_info.build_records(template=s, title=n)
            for i, row in database_info.records.iterrows():
                
                #yield an iprPy.Record object
                yield Record(s, n, row.content.encode('utf-8'))
    
def get_records(database_info, name=None, style=None):
    """Retrieves records from a database"""
    
    #Transform iterator into list
    return [i for i in iget_records(database_info, name=name, style=style)]

def get_record(self, name=None, style=None):
    """Returns a single record matching given conditions. Issues an error if none or multiple matches are found."""
    
    #Get records
    record = get_records(name=name, style=style)
    
    #Verify that there is only one matching record
    if len(record) == 1:
        return record[0]
    elif len(record) == 0:
        raise ValueError('Cannot find matching record')
    else:
        raise ValueError('Multiple matching records found')
        
def add_record(database_info, record=None, style=None, name=None, content=None):
    """Adds a new record to a database"""
    
    #Create Record object if not given
    if record is None:
        record = Record(style, name, content)
    
    #Issue a TypeError for competing kwargs
    elif style is not None or name is not None or content is not None:
        raise TypeError('kwargs style, name, and content cannot be given with kwarg record')
        
    #Verify that there isn't already a record with a matching name
    if len(get_records(database_info, name=record.name)) > 0:
        raise ValueError('Record ' + record.name + ' already exists')
    
    #upload record to database
    database_info.add_record(record.content, record.name, record.style, refresh=False)
    
    return record
    
def update_record(database_info, record=None, style=None, name=None, content=None):
    """Updates an existing record in a database"""
    
    #Create Record object if not given
    if record is None:
        if content is None:
            raise TypeError('no new content given')
        oldrecord = self.get_record(name=name, style=style)
        record = Record(oldrecord.style, oldrecord.name, content)
    
    #Issue a TypeError for competing kwargs
    elif style is not None or name is not None:
        raise TypeError('kwargs style and name cannot be given with kwarg record')
    
    #Replace content in record object
    elif content is not None:
        oldrecord = record
        record = Record(oldrecord.style, oldrecord.name, content)
        
    #Find oldrecord matching record
    else:
        oldrecord = self.get_record(name=record.name, style=record.style)
    
    database_info.update_record(oldrecord.name, record.content, refresh=False)
    
    return record
    
def delete_record(database_info, record=None, name=None, style=None):
    """deletes an existing record in a database"""
    
    #Create Record object if not given
    if record is None:
        record = get_record(name=name, style=style)
    
    #Issue a TypeError for competing kwargs
    elif style is not None or name is not None:
        raise TypeError('kwargs style and name cannot be given with kwarg record')
    
    #Verify that record exists
    else:
        record = get_record(name=record.name, style=record.style)
    
    #Delete record
    database_info.delete_record(record.name, refresh=False)
    
def add_tar(database_info, record=None, name=None, style=None, root_dir=None):
    """Archives calculation folder as a tar file and saves to the database"""

    #Create Record object if not given
    if record is None:
        record = get_record(name=name, style=style)
    
    #Issue a TypeError for competing kwargs
    elif style is not None or name is not None:
        raise TypeError('kwargs style and name cannot be given with kwarg record')
    
    #Verify that record exists
    else:
        record = get_record(name=record.name, style=record.style)
    
    #build path to record
    record_path = os.path.join(database_info, record.style, record.name)
    
    #Check if an archive already exists
    model = DM(record.content)
    if len(record.finds('archive')) == 0:
        raise ValueError('Record already has an archive')
    
    #Make archive
    shutil.make_archive(record.name, 'gztar', root_dir=root_dir, base_dir=record.name) 
    
    #Upload archive
    root_key = model.keys()[0]
    model[root_key]['archive'] = DM()
    model[root_key]['archive']['url'] = database_info.add_file(record.name+'.tar.gz')
    
    update_record(database_info, name=record.name, style=record.style, content=model.xml())
    
    #Remove local archive copy
    os.remove(record.name+'.tar.gz')
    

def get_tar(database_info, record=None, name=None, style=None):
    """Retrives a stored calculation tar archive"""

    #Create Record object if not given
    if record is None:
        record = get_record(name=name, style=style)
    
    #Issue a TypeError for competing kwargs
    elif style is not None or name is not None:
        raise TypeError('kwargs style and name cannot be given with kwarg record')
    
    #Verify that record exists
    else:
        record = get_record(name=record.name, style=record.style)
    
    #Extract url to tar file
    model = DM(record.content)
    url = model.find('archive')['url']
        
    return tarfile.open(fileobj = BytesIO(database_info.get_file(url)))    
    