# Standard Python libraries
from pathlib import Path

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from ..tools import screen_input

class Settings():
    """
    Class for handling iprPy settings.
    """
    def __init__(self):
        """
        Class initializer. Calls load.
        """
        self.load()

    @property
    def defaultdirectory(self):
        """pathlib.Path : Path to the default iprPy settings directory"""
        return Path(Path.home(), '.iprPy')

    @property
    def defaultfilename(self):
        """pathlib.Path : Path to the default iprPy settings.json file"""
        return Path(self.defaultdirectory, 'settings.json')

    @property
    def directory(self):
        """pathlib.Path : Path to the iprPy settings directory"""
        return self.__directory

    @property
    def filename(self):
        """pathlib.Path : Path to the iprPy settings.json file"""
        return Path(self.directory, 'settings.json')

    @property
    def library_directory(self):
        """pathlib.Path : Path to the iprPy library directory."""
        
        # Check library_directory value
        if 'library_directory' in self.__content:
            return Path(self.__content['library_directory'])
        else:
            return Path(self.directory, 'library')

    @property
    def runner_log_directory(self):
        """pathlib.Path : Path to the directory where runner logs are saved to."""

        # Check runner_log_directory value
        if 'runner_log_directory' in self.__content:
            return Path(self.__content['runner_log_directory'])
        else:
            return Path(self.directory, 'runner-logs')

    @property
    def databases(self):
        """dict: The pre-defined database settings organized by name"""
        databases = {}
        for database in self.__content.aslist('database'):
            name = database['name']

            databases[name] = {}
            databases[name]['style'] = database['style']
            databases[name]['host'] = database['host']
            
            for param in database.aslist('params'):
                for key, value in param.items():
                    databases[name][key] = value
        return databases

    @property
    def list_databases(self):
        """list: The names of the pre-defined database names"""
        return list(self.databases.keys())

    @property
    def run_directories(self):
        """dict: The pre-defined run_directory paths organized by name"""
        run_directories = {}
        for run_directory in self.__content.aslist('run_directory'):
            run_directories[run_directory['name']] = run_directory['path']
        
        return run_directories

    @property
    def list_run_directories(self):
        """list: The names of the pre-defined database names"""
        return list(self.run_directories.keys())
        
    def load(self):
        """
        Loads the settings.json file.
        """
        # Load settings.json from the default location
        if self.defaultfilename.is_file():
            self.__defaultcontent = DM(self.defaultfilename)['iprPy-defined-parameters']
        else:
            self.__defaultcontent = DM()
            
        # Check if forwarding_directory has been set
        if 'forwarding_directory' in self.__defaultcontent:
            self.__directory = Path(self.__defaultcontent['forwarding_directory'])
            
            # Load content from the forwarded location
            if self.filename.is_file():
                self.__content = DM(self.filename)['iprPy-defined-parameters']
            else:
                self.__content = DM()

            # Check for recursive forwarding
            if 'forwarding_directory' in self.__content:
                raise ValueError('Multi-level forwarding not allowed.')
        
        # If no forwarding, default is current content
        else:
            self.__content = self.__defaultcontent
            self.__directory = self.defaultdirectory

    def save(self):
        """
        Saves current settings to settings.json.
        """
        settings = DM()
        settings['iprPy-defined-parameters'] = self.__content
    
        if not self.directory.is_dir():
            self.directory.mkdir(parents=True)

        with open(self.filename, 'w') as f:
            settings.json(fp=f, indent=4)
        
        # Reload
        self.load()

    def defaultsave(self):
        """
        Saves settings to the default settings.json.  Used by forwarding
        methods.
        """
        settings = DM()
        settings['iprPy-defined-parameters'] = self.__defaultcontent
    
        if not self.defaultdirectory.is_dir():
            self.defaultdirectory.mkdir(parents=True)

        with open(self.defaultfilename, 'w') as f:
            settings.json(fp=f, indent=4)   
        
        # Reload
        self.load()

    def set_directory(self, path=None):
        """
        Sets settings directory to a different location.

        Parameters
        ----------
        path : str or Path
            The path to the new settings directory where settings.json (and the
            default library directory) are to be located.
        """
        # Check if a different directory has already been set
        if 'forwarding_directory' in self.__defaultcontent:
            print(f'Settings directory already set to {self.directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        elif len(self.__defaultcontent) != 0:
            raise ValueError(f'directory cannot be set if other settings exist in {self.defaultfilename}')

        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the new settings directory:")
        self.__defaultcontent['forwarding_directory'] = Path(path).resolve().as_posix()
                
        # Save changes to default
        self.defaultsave()
        
    def unset_directory(self):
        """
        Resets settings directory information back to the default <home>/.iprPy/ location.
        """
        
        # Check if forwarding_directory has been set
        if 'forwarding_directory' not in self.__defaultcontent:
            print(f'No settings directory set, still using default {self.defaultdirectory}')
        
        else:
            print(f'Remove settings directory {self.directory} and reset to {self.defaultdirectory}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__defaultcontent['forwarding_directory']

            # Save changes to default
            self.defaultsave()
            
    def set_library_directory(self, path=None):
        """
        Sets the library directory to a different location.

        Parameters
        ----------
        path : str or Path
            The path to the new library directory where reference files are to be located.
            If not given, will be asked for in a prompt.
        """
        # Check if a different directory has already been set
        if 'library_directory' in self.__content:
            print(f'Library directory already set to {self.library_directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the new library directory:")
        self.__content['library_directory'] = Path(path).resolve().as_posix()

        # Save changes
        self.save()
        
    def unset_library_directory(self):
        """
        Resets the saved library directory information back to the default
        <Settings.directory>/library/ location.
        """
        
        # Check if library_directory has been set
        if 'library_directory' not in self.__content:
            print(f'Library directory not set: still using {self.library_directory}')
        
        else:
            print(f'Remove library directory {self.library_directory} and reset to {Path(self.directory, "library")}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__content['library_directory']

            # Save changes
            self.save()
                  
    def set_runner_log_directory(self, path=None):
        """
        Sets the runner log directory to a different location.

        Parameters
        ----------
        path : str or Path
            The path to the new runner log directory where log files generated
            by runners are saved to.  If not given, will be asked for in a
            prompt.
        """
        # Check if a different directory has already been set
        if 'runner_log_directory' in self.__content:
            print(f'Runner log directory already set to {self.runner_log_directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the new runner log directory:")
        self.__content['runner_log_directory'] = Path(path).resolve().as_posix()

        # Save changes
        self.save()
        
    def unset_runner_log_directory(self):
        """
        Resets the saved runner log directory information back to the default
        <Settings.directory>/runner-logs/ location.
        """
        
        # Check if library_directory has been set
        if 'runner_log_directory' not in self.__content:
            print(f'Runner log directory not set: still using {self.runner_log_directory}')
        
        else:
            print(f'Remove runner log directory {self.runner_log_directory} and reset to {Path(self.directory, "runner-logs")}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__content['runner_log_directory']

            # Save changes
            self.save()

    def set_database(self, name=None, style=None, host=None, **kwargs):
        """
        Allows for database information to be defined in the settings file. Screen
        prompts will be given to allow any necessary database parameters to be
        entered.

        Parameters
        ----------
        name : str, optional
            The name to assign to the database. If not given, the user will be
            prompted to enter one.
        style : str, optional
            The database style associated with the database. If not given, the
            user will be prompted to enter one.
        host : str, optional
            The database host (directory path or url) where the database is
            located. If not given, the user will be prompted to enter one.
        **kwargs : any, optional
            Any other database style-specific parameter settings required to
            properly access the database.
        """
        # Ask for name if not given
        if name is None:
            name = screen_input('Enter a name for the database:')

        # Load database if it exists
        if name in self.list_databases:
            
           # Ask if existing database should be overwritten
            print('Database', name, 'already defined.')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                database_settings = self.__content.find('database', yes={'name':name})
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
                 
        # Create new database entry if it doesn't exist
        else:
            database_settings = DM()
            self.__content.append('database', database_settings)
            database_settings['name'] = name
            
        # Ask for style if not given
        if style is None: 
            style = screen_input("Enter the database's style:")
        database_settings['style'] = style

        #Ask for host if not given
        if host is None:
            host = screen_input("Enter the database's host:")
        database_settings['host'] = str(host)

        # Ask for additional kwargs if not given
        if len(kwargs) == 0:
            print('Enter any other database parameters as key, value')
            print('Exit by leaving key blank')
            while True:
                key = screen_input('key:')
                if key == '': 
                    break
                kwargs[key] = screen_input('value:')
        for key, value in kwargs.items():
            database_settings.append('params', DM([(key, value)]))

        # Save changes
        self.save()
    
    def unset_database(self, name=None):
        """
        Deletes the settings for a pre-defined database from the settings file.

        Parameters
        ----------
        name : str
            The name assigned to a pre-defined database.
        """
        database_names = self.list_databases
                  
        # Ask for name if not given
        if name is None:
            
            if len(database_names) > 0:
                print('Select a database:')
                for i, database in enumerate(database_names):
                    print(i+1, database)
                choice = screen_input(':')
                try:
                    choice = int(choice)
                except:
                    name = choice
                else:
                    name = database_names[choice-1]
            else:
                print('No databases currently set')
                return None

        # Verify listed name exists 
        try:
            i = database_names.index(name)
        except:
            raise ValueError(f'Database {name} not found')

        print(f'Database {name} found')
        test = screen_input('Delete settings? (must type yes):').lower()
        if test == 'yes':
            if len(database_names) == 1:
                del(self.__content['database'])
            else:
                self.__content['database'].pop(i)
                if len(self.__content['database']) == 1:
                    self.__content['database'] = self.__content['database'][0]
                  
            self.save()
                  
    def set_run_directory(self, name=None, path=None):
        """
        Allows for run_directory information to be defined in the settings file.

        Parameters
        ----------
        name : str, optional
            The name to assign to the run_directory.  If not given, the user will
            be prompted to enter one.
        path : str, optional
            The directory path for the run_directory.  If not given, the user will
            be prompted to enter one.
        """
                  
        # Ask for name if not given
        if name is None:
            name = screen_input('Enter a name for the run_directory:')

        # Load run_directory if it exists
        if name in self.list_run_directories:
            
            # Ask if existing run_directory should be overwritten     
            print(f'run_directory {name} already defined.')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                run_directory_settings = self.__content.find('run_directory', yes={'name':name})
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Create new run_directory entry if it doesn't exist
        else: 
            run_directory_settings = DM()
            self.__content.append('run_directory', run_directory_settings)
            run_directory_settings['name'] = name

        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the run_directory's path:")
        run_directory_settings['path'] = Path(path).resolve().as_posix()

        self.save()

    def unset_run_directory(self, name=None):
        """
        Deletes the settings for a pre-defined run_directory from the settings
        file.

        Parameters
        ----------
        name : str
            The name assigned to a pre-defined run_directory.
        """
        run_directory_names = self.list_run_directories

        # Ask for name if not given
        if name is None:
            if len(run_directory_names) > 0:
                print('Select a run_directory:')
                for i, run_directory in enumerate(run_directory_names):
                    print(i+1, run_directory)
                choice = screen_input(':')
                try:
                    choice = int(choice)
                except:
                    name = choice
                else:
                    name = run_directory_names[choice-1]
            else:
                print('No run_directories currently set')
                return None

        # Verify listed name exists 
        try:
            i = run_directory_names.index(name)
        except:
            raise ValueError(f'Run directory {name} not found')

        print(f'Run directory {name} found')
        test = screen_input('Delete settings? (must type yes):').lower()
        if test == 'yes':
            if len(run_directory_names) == 1:
                del(self.__content['run_directory'])
            else:
                self.__content['run_directory'].pop(i)
                if len(self.__content['run_directory']) == 1:
                    self.__content['run_directory'] = self.__content['run_directory'][0]
                  
            self.save()