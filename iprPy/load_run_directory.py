# coding: utf-8

# Standard Python libraries
from pathlib import Path
from typing import Optional

# iprPy imports
from . import settings
from .tools import screen_input

def load_run_directory(name: Optional[str] = None):
    """
    Loads a pre-defined run_directory from the settings file.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined run_directory.
    
    Returns
    -------
    str
        The path to the identified run_directory.
    """
    # Ask for name if not given
    if name is None:
        run_directory_names = settings.list_run_directories
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
            raise KeyError('No run_directories currently set')

    try:
        return Path(settings.run_directories[name])
    except:
        raise ValueError(f'run_directory {name} not found')