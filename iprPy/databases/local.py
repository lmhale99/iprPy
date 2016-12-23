import os
import glob
import shutil
import tarfile

from iprPy.tools import iaslist

def initialize(path):
    """Initializes access to a local database by checking that the supplied path is or can be a directory"""
    
    database_info = os.path.abspath(path)
    
    if not os.path.isdir(database_info):
        os.makedirs(database_info)
        
    return database_info    
    
def iget_records(database_info, record_type=None, key=None):
    """Iterates through matching records in the database"""
    
    if record_type is None: record_type = ['*']
    if key is None: key = ['*']
    ext = ['.xml']
    
    record_paths = []
    
    for rtype in iaslist(record_type):
        for k in iaslist(key):
            for e in iaslist(ext):
                for record in glob.iglob(os.path.join(database_info, rtype, k+e)):
                    with open(record) as f:
                        yield f.read()
    
def get_records(database_info, record_type=None, key=None):
    """Retrieves records from a database"""
    
    return [i for i in iget_records(database_info, record_type, key)]
    
def add_record(database_info, record_data, record_type, key):
    """Adds a new record to a database"""
    
    if not os.path.isdir(os.path.join(database_info, record_type)):
        os.mkdir(os.path.join(database_info, record_type))
    
    if len(get_records(database_info, key=key)) > 0:
        raise ValueError('Record ' + key + ' already exists')
    
    with open(os.path.join(database_info, record_type, key+'.xml'), 'w') as f:
        f.write(record_data)    
       
def update_record(database_info, record_data, key):
    """Updates an existing record in a database"""
    
    record_path = glob.glob(os.path.join(database_info, '*', key+'.xml'))
    
    if len(record_path) == 1:
        record_path = record_path[0]
        with open(record_path, 'w') as f:
            f.write(record_data)
    
    elif len(record_path) == 0:
        raise ValueError('Record ' + key + ' not found')
    else:
        raise ValueError('Multiple records for ' + key + ' found')       
    
def delete_record(database_info, key):
    """deletes an existing record in a database"""
    
    #Find path to record
    record_path = glob.glob(os.path.join(database_info, '*', key+'.xml'))
    
    #If exactly one match is found, delete the file
    if len(record_path) == 1:
        record_path = record_path[0]
        os.remove(record_path)
    
    
    elif len(record_path) == 0:
        raise ValueError('Record for' + key + ' not found')
    
    else:
        raise ValueError('Multiple records for ' + key + ' found') 
        
def add_archive(database_info, root_directory, key):
    """Archives calculation folder and saves to the database"""

    #Find path to record
    record_path = glob.glob(os.path.join(database_info, '*', key+'.xml'))
    
    #If exactly one match is found, add archive with matching name
    if len(record_path) == 1:
        record_path = record_path[0]
        archive_path = os.path.splitext(record_path)[0]
        
        #Check if an archive already exists
        assert not os.path.isfile(archive_path+'.tar.gz'), 'Record already has an archive'
        
        #Make archive
        shutil.make_archive(archive_path, 'gztar', root_dir=root_directory, base_dir=key)        
    
    elif len(record_path) == 0:
        raise ValueError('Record for ' + key + ' not found')
    else:
        raise ValueError('Multiple records for ' + key + ' found') 
    
    
    
    

def get_archive(database_info, key):
    """Retrives a stored calculation archive"""

    #Find path to archive
    archive_path = glob.glob(os.path.join(database_info, '*', key+'.tar.gz'))
    
    #If exactly one match is found, return it
    if len(archive_path) == 1:
        archive_path = archive_path[0]
        
        return tarfile.open(archive_path)
    
    
    elif len(archive_path) == 0:
        raise ValueError('Archive for ' + key + ' not found')
    
    else:
        raise ValueError('Multiple archives for ' + key + ' found') 




