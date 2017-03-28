from __future__ import print_function
import os
import sys
from DataModelDict import DataModelDict as DM

from iprPy import Database, rootdir
from iprPy.tools import screen_input

settingsfile = os.path.join(rootdir, '.iprPy')

def load_settings():
    """Loads the .iprPy settings file"""
    
    #Load settings file if it exists
    try:
        with open(settingsfile, 'r') as f:
            settings = DM(f)
    
    #Create a new settings file if it doesn't exist
    except:
        settings = DM()
        settings['iprPy-defined-parameters'] = DM()
        #settings['iprPy-defined-parameters']['database'] = DM()
        #settings['iprPy-defined-parameters']['run_directory'] = DM()
        with open(settingsfile, 'w') as f:
            settings.json(fp=f, indent=4)
            
    return settings
        
def get_database(name=None):
    """Loads a pre-defined database from the settings file"""
    
    #Get information from settings file
    settings = load_settings()
    
    #Ask for name if not given
    if name is None:
        databases = settings['iprPy-defined-parameters'].aslist('database')
        if len(databases) > 0:
            print('Select a database:')
            for i, database in enumerate(databases):
                print(i+1, database['name'])
            choice = screen_input(':')
            try:
                choice = int(choice)
            except:
                name = choice
            else:
                name = databases[choice-1]['name']
        else:
            print('No databases currently set')
            sys.exit()
    
    #Get the appropriate database
    try:
        database_settings = settings.find('database', yes={'name':name})
    except:
        raise ValueError('Database '+ name + ' not found')
    
    #Extract parameters
    style = database_settings['style']
    host = database_settings['host']
    params = {}
    for param in database_settings.aslist('params'):
        key = param.keys()[0]
        params[key] = param[key]
    
    #Load database
    return Database(style, host, **params)
        
def set_database(name=None, style=None, host=None):
    """Allows for database access information to be saved in a settings file"""
    
    #Get information from the settings file
    settings = load_settings()
    
    #Find existing database definitions
    databases = settings['iprPy-defined-parameters'].aslist('database')
    
    #Ask for name if not given
    if name is None:
        name = screen_input('Enter a name for the database:')
        
    #Load database if it exists
    try: database_settings = settings.find('database', yes={'name':name})
    
    #Create new database entry if it doesn't exist    
    except: 
        database_settings = DM()
        settings['iprPy-defined-parameters'].append('database', database_settings)
        database_settings['name'] = name        
    
    #Ask if existing database should be overwritten    
    else: 
        print('Database', name, 'already defined.')
        option = screen_input('Overwrite? (yes or no):')
        if option in ['yes', 'y']:  pass
        elif option in ['no', 'n']: return None
        else: raise ValueError('Invalid choice')
            
    #Ask for style if not given
    if style is None: style = screen_input("Enter the database's style:")
    database_settings['style'] = style
    
    #Ask for host if not given
    if host is None:  host = screen_input("Enter the database's host:")
    database_settings['host'] = host
    
    print('Enter any other database parameters as key, value')
    print('Exit by leaving key blank')
    
    while True:
        key = screen_input('key:')
        if key == '': break
        value = screen_input('value:')
        database_settings.append('params', DM([(key, value)]))
        
    with open(settingsfile, 'w') as f:
        settings.json(fp=f, indent=4)

def unset_database(name=None):
    """Removes a pre-defined database from the settings file"""
    
    #Get information from settings file
    settings = load_settings()
    
    #Ask for name if not given
    if name is None:
        databases = settings['iprPy-defined-parameters'].aslist('database')
        if len(databases) > 0:
            print('Select a database:')
            for i, database in enumerate(databases):
                print(i+1, database['name'])
            choice = screen_input(':')
            try:
                choice = int(choice)
            except:
                name = choice
            else:
                name = databases[choice-1]['name']
        else:
            print('No databases currently set')
            sys.exit()
            
    print('Database', name, 'found')
    test = iprPy.tools.screen_input('Delete database? (must type yes):')
    if test == 'yes':
        if len(databases) == 1:
            del(settings['iprPy-defined-parameters']['database'])
        else:
            new = DM()
            for database in databases:
                if database['name'] != name:
                    new.append('database', database)
            settings['iprPy-defined-parameters']['database'] = new['database']
            
        with open(settingsfile, 'w') as f:
            settings.json(fp=f, indent=4)
        print('database', name, 'successfully deleted')
    
def get_run_directory(name=None):
    """Loads a pre-defined run_directory from the settings file"""
    
    #Get information from settings file
    settings = load_settings()
    
    #Ask for name if not given
    if name is None:
        run_directories = settings['iprPy-defined-parameters'].aslist('run_directory')
        if len(run_directories) > 0:
            print('Select a run_directory:')
            for i, run_directory in enumerate(run_directories):
                print(i+1, run_directory['name'])
            choice = screen_input(':')
            try:
                choice = int(choice)
            except:
                name = choice
            else:
                name = run_directories[choice-1]['name']
        else:
            print('No run_directories currently set')
            sys.exit()
    
    #Get the appropriate database
    try:
        run_directory_settings = settings.find('run_directory', yes={'name':name})
    except:
        raise ValueError('run_directory '+ name + ' not found')
    
    #Extract parameters
    return run_directory_settings['path']
        
def set_run_directory(name=None, path=None):
    """Allows for run_directory information to be saved in a settings file"""
    
    #Get information from the settings file
    settings = load_settings()
    
    #Find existing run_directory definitions
    run_directories = settings['iprPy-defined-parameters'].aslist('run_directory')
    
    #Ask for name if not given
    if name is None:
        name = screen_input('Enter a name for the run_directory:')
        
    #Load run_directory if it exists
    try: run_directory_settings = settings.find('run_directory', yes={'name':name})
    
    #Create new run_directory entry if it doesn't exist    
    except: 
        run_directory_settings = DM()
        settings['iprPy-defined-parameters'].append('run_directory', run_directory_settings)
        run_directory_settings['name'] = name
    
    #Ask if existing run_directory should be overwritten    
    else: 
        print('run_directory', name, 'already defined.')
        option = screen_input('Overwrite? (yes or no):')
        if option in ['yes', 'y']:  pass
        elif option in ['no', 'n']: return None
        else: raise ValueError('Invalid choice')
            
    #Ask for path if not given
    if path is None: path = screen_input("Enter the run_directory's path:")
    run_directory_settings['path'] = path
        
    with open(settingsfile, 'w') as f:
        settings.json(fp=f, indent=4)