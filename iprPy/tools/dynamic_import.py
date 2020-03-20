from importlib import import_module, resources
from pathlib import Path
import sys

def dynamic_import(module_name, ignorelist=None):
    """
    Dynamically imports classes stored in submodules and makes them directly
    accessible by style name within the returned loaded dictionary.
    
    Parameters
    ----------
    module_name : str
        The name of the module to start from
    ignorelist : list, optional
        A list of submodules that should be excluded from the import.

    Returns
    -------
    loaded : dict
        Contains the derived classes that were successfully loaded and
        accessible by style name (root submodule).
    failed : dict
        Contains the raised error messages for each class that failed
        to load.
    """
    # Handle ignorelist
    if ignorelist is None:
        ignorelist = []
    ignorelist = ['__init__', '__pycache__'] + ignorelist
    
    # Identify names of submodules to try loading
    names = []
    for child in resources.contents(module_name):
        child = Path(child)
        
        if child.suffix.lower() in ('.py', '.pyc', ''):
            name = child.stem
            if name not in ignorelist and name not in names:
                names.append(name)
    
    # Try loading submodules
    loaded = {}
    failed = {}
    for name in names:
        try:
            module = import_module('.' + name, module_name)
            all = getattr(module, '__all__')
            if len(all) != 1:
                raise AttributeError("module's __all__ must have only one attribute")
        except:
            failed[name] = '%s: %s' % sys.exc_info()[:2]
        else:
            loaded[name] = getattr(module, all[0])
    
    return loaded, failed