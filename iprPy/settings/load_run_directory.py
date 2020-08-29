from pathlib import Path

from . import Settings
from ..tools import screen_input

def load_run_directory(name=None):
    """
    Loads a pre-defined run_directory from the settings file.
    
    Parameters
    ----------
    name : str
        The name assigned to a pre-defined run_directory.
    
    Returns
    -------
    str
        The path to the identified run_directory.
    """
    # Get information from settings file'
    settings = Settings()
    run_directory_names = settings.list_run_directories

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
            raise KeyError('No run_directories currently set')

    try:
        return Path(settings.run_directories[name])
    except:
        raise ValueError(f'run_directory {name} not found')