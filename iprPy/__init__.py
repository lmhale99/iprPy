"""
Attributes
----------
rootdir : str
    The absolute path to the iprPy package's root directory used to locate
    contained data files.
libdir : str
    The absolute path to the iprPy package's library directory.
"""
# Standard Python libraries
from pathlib import Path
from importlib import resources

# Define package-specific directories
rootdir = Path(__file__).absolute().parent
contentdir = Path(Path.home(), '.iprPy')
libdir = Path(contentdir, 'library')

# Read version from VERSION file
__version__ = resources.read_text('iprPy', 'VERSION').strip()

__all__ = ['__version__', 'rootdir', 'libdir', 'tools', 'input',
           'record', 'load_record', 'calculation', 'load_calculation',
           'database', 'list_databases', 'load_database', 'set_database',
           'unset_database', 'list_run_directories',
           'load_run_directory', 'set_run_directory', 'unset_run_directory',
           'analysis', 'workflow', 'check_modules']
__all__.sort()

# iprPy imports
from . import tools
from . import analysis

from . import input

from . import record
from .record import load_record

from . import calculation
from .calculation import load_calculation

from . import database
from .database import (list_databases, load_database, set_database, unset_database,
                       list_run_directories, load_run_directory, set_run_directory,
                       unset_run_directory)


from . import workflow

from .check_modules import check_modules