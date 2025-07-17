from io import IOBase
import sys
from pathlib import Path
from importlib import import_module, resources
from typing import Optional, Union

from yabadaba.tools import ModuleManager, is_uuid

calculationmanager = ModuleManager('Calculation')
from .. import recordmanager

from .Calculation import Calculation

__all__ = ['Calculation', 'calculationmanager', 'load_calculation']

# Define subfolders to ignore
ignorelist = ['__pycache__', 'subsets']

# Dynamically import calculation styles
for style in resources.contents(__name__):

    # Only import subfolders not in ignorelist
    if '.' not in style and style not in ignorelist:
        try:
            # Try importing calculation
            module = import_module(f'.{style}', __name__)
            classname = module.__all__[0]
            classmodule = getattr(module, classname)
            classname = module.__all__[0]
            classmodule = getattr(module, classname)
            
        except Exception as e:
            # Add failed imports to managers
            recordmanager.failed_styles[f'calculation_{style}'] = '%s: %s' % sys.exc_info()[:2]
            calculationmanager.failed_styles[style] = '%s: %s' % sys.exc_info()[:2]

        else:
            # Add successful imports to managers
            recordmanager.loaded_styles[f'calculation_{style}'] = classmodule
            calculationmanager.loaded_styles[style] = classmodule

def load_calculation(style, **kwargs):
    """
    Loads a Calculation subclass associated with a given calculation style

    Parameters
    ----------
    style : str
        The calculation style
    
    Returns
    -------
    subclass of iprPy.calculation.Calculation 
        A Calculation object for the style
    """
    return calculationmanager.init(style, **kwargs)

def run_calculation(params: Union[str, dict, IOBase, None] = None,
                    calc_style: Optional[str] = None,
                    calc_key: Optional[str] = None,
                    raise_error: bool = False,
                    verbose: bool = True):
    """
    Runs a calculation from a parameter file and outputs results to
    results.json.

    Parameters
    ----------
    params : dict, str or file-like object, optional
        The parameters or parameter file to read in.  If not given, will
        run based on the current object attribute values.
    calc_style : str, optional
        Specifies the style of calculation to run.  Optional if params is a
        path to a file where the file's name is calc_<calc_style>.in.
    calc_key : str, optional
        Allows for a calculation UUID key to be passed in.  If not given, then
        will check if the parent directory's name is a UUID key and will use it
        if possible.  Otherwise, a new UUID key will be assigned to the
        calculation.
    raise_error : bool, optional
        The default behavior of run is to take any error messages from the
        calculation and set them to class attributes and save to
        results.json. This allows for calculations to successfully fail.
        Setting this to True will instead raise the errors, which can
        provide more details for debugging.
    verbose : bool, optional
        If True, a message relating to the calculation's status will be
        printed upon completion.  Default value is True.
    """
    if calc_style is None:
        # Extract calc_style from filename
        if isinstance(params, (str, Path)):
            calc_style = Path(params).stem.replace('calc_', '')
        else:
            raise ValueError('calc_style not given and cannot be determined from params')

    kwargs = {}
    if calc_key is None:
        
        # If params is a file, check if its parent directory name is a uuid key
        if isinstance(params, (str, Path)):
            calc_key = Path(params).absolute().parent.name
        
        # Otherwise, check the name of the working directory
        else:
            calc_key = Path('.').absolute().name
        
        if is_uuid(calc_key):
            kwargs['key'] = calc_key

    
    else:
        # Check that given calc_key is a valid uuid key
        if not is_uuid(calc_key):
            raise ValueError('calc_key must be a uuid key!')
        kwargs['key'] = calc_key


    # Load calculation style and read in paramfile
    calculation = load_calculation(calc_style, params=params, **kwargs)
    
    # Run and create results_json
    calculation.run(results_json=True, raise_error=raise_error, verbose=verbose)
    