import os
import glob
import shutil
import tarfile

from iprPy.tools import iaslist
from iprPy import Record

def initialize(host):
    """Initializes access to a local database by checking that the supplied path is or can be a directory"""
    
    #database_info is simply a local directory path
    database_info = os.path.abspath(host)
    
    #Make the directory path if needed
    if not os.path.isdir(database_info):
        os.makedirs(database_info)
        
    return database_info    
    
def iget_records(database_info, name=None, style=None):
    """Iterates through matching records in the database"""
    
    #Set default search parameters
    if style is None: style = ['*']
    if name is None: name = ['*']
    
    #iterate through all files matching style, name, ext values
    for s in iaslist(style):
        for n in iaslist(name):
            for ext in iaslist(['.xml']):
                for rfile in glob.iglob(os.path.join(database_info, s, n+ext)):
                    
                    #Open record file and yield an iprPy.Record object
                    with open(rfile) as f:
                        yield Record(s, n, f.read())
    
def get_records(database_info, name=None, style=None):
    """Retrieves records from a database"""
    
    #Transform iterator into list
    return [i for i in iget_records(database_info, name=name, style=style)]

def get_record(self, name=None, style=None):
    """Returns a single record matching given conditions. Issues an error if none or multiple matches are found."""
    
    #get records
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
    
    #Make record style directory if needed
    if not os.path.isdir(os.path.join(database_info, record.style)):
        os.mkdir(os.path.join(database_info, record.style))
    
    #Save content to an .xml file 
    with open(os.path.join(database_info, record.style, record.name+'.xml'), 'w') as f:
        f.write(record.content)
        
    return record
       
def update_record(database_info, record=None, style=None, name=None, content=None):
    """Updates the content of an existing record in the database"""
    
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
    
    #Delete oldrecord
    delete_record(database_info, record=oldrecord)

    #Add new record
    add_record(database_info, record=record)
    
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
    
    #build path to record
    record_path = os.path.join(database_info, record.style, record.name)

    #Delete record file
    os.remove(record_path+'.xml')
        
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
    if os.path.isfile(record_path+'.tar.gz'):
        raise ValueError('Record already has an archive')
        
    #Make archive
    shutil.make_archive(record_path, 'gztar', root_dir=root_dir, base_dir=record.name)         

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
    
    #build path to record
    record_path = os.path.join(database_info, record.style, record.name)
    
    return tarfile.open(record_path+'.tar.gz')