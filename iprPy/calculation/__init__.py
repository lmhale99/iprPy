import sys
from pathlib import Path
from importlib import import_module, resources

from datamodelbase.tools import ModuleManager

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
            
        except Exception as e:
            # Add failed imports to managers
            recordmanager.failed_styles[f'calculation_{style}'] = '%s: %s' % sys.exc_info()[:2]
            calculationmanager.failed_styles[style] = '%s: %s' % sys.exc_info()[:2]

        else:
            # Add successful imports to managers
            classname = module.__all__[0]
            classmodule = getattr(module, classname)
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

def run_paramfile2json(filename, calculation=None):
    """
    Runs a calculation from a parameter file and outputs results to
    results.json.

    Parameters
    ----------
    filename : str
        The path to a parameter file to read.  The file's name should start
        with "calc_" followed by the calculation's calc_style.
    calculation : iprPy.Calculation, optional
        Allows for an existing calculation object to be used.  If not given,
        then a new calculation object will be created.

    Returns
    -------
    status : str
        The calculation's status ('finished' or 'error') after running.
    error : str or None
        Any error message thrown by the calculation.
    """
    # Extract calc_style from filename
    calc_style = Path(filename).stem.replace('calc_', '')
    
    # Load calculation style and read in paramfile
    calculation = load_calculation(calc_style, params=filename)
    
    # Run and create results_json
    calculation.run(results_json=True)
    
    return calculation.status, calculation.error
