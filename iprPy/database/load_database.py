# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from ..tools import screen_input
from . import loaded
from .settings import load_settings

__all__ = ['load_database']

def load_database(name=None, style=None, host=None, **kwargs):
    """
    Loads a database object.  Can be either loaded from stored settings or
    by defining all needed access information.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined database.  If given, can be the only
        parameter.
    style : str, optional
        The database style to use.
    host : str, optional
        The URL/file path where the database is hosted.
    kwargs : dict, optional
        Any other keyword parameters defining necessary access information.
        Allowed keywords are database style-specific.
    
    Returns
    -------
    Subclass of iprPy.Database
        The database object.
    """
    
    # Ask for name if no parameters given
    if name is None and style is None and host is None and len(kwargs) == 0:
        
        # Get information from settings file
        settings = load_settings()
        
        # Find matching database name
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
            raise KeyError('No databases currently set')
    
    if name is not None:
        if style is None and host is None and len(kwargs) == 0:
            
            # Get information from settings file
            settings = load_settings()
            
            # Get the appropriate database
            try:
                database_settings = settings.find('database', yes={'name':name})
            except:
                raise KeyError('Database '+ name + ' not found')
            
            # Extract parameters
            style = database_settings['style']
            host = database_settings['host']
            kwargs = {}
            for param in database_settings.aslist('params'):
                key = list(param.keys())[0]
                kwargs[key] = param[key]
        else:
            raise ValueError('name cannot be given with any other parameters')
    
    # return database
    if style in loaded:
        return loaded[style](host, **kwargs)
    else:
        raise KeyError('Unknown database style ' + style)