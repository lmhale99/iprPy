"""
Attributes
----------
rootdir : str
    The absolute path to the iprPy package's root directory used to locate
    contained data files.
"""
# Standard Python libraries
from __future__ import division, absolute_import, print_function
import os

# Read version from VERSION file
with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

__all__ = ['__version__', 'rootdir', 'compatibility', 'tools', 'input',
           'record', 'load_record', 'calculation', 'load_calculation',
           'database', 'load_database', 'set_database', 'unset_database',
           'load_run_directory', 'set_run_directory', 'unset_run_directory',
           'analysis', 'check_modules']
__all__.sort()

# Define root package directory
rootdir = os.path.dirname(os.path.abspath(__file__))

# iprPy imports
from . import compatibility
from . import tools
from . import input

from . import record
from .record import load_record

from . import calculation
from .calculation import load_calculation

from . import database
from .database import (load_database, set_database, unset_database,
                       load_run_directory, set_run_directory,
                       unset_run_directory)

from . import analysis

from .check_modules import check_modules