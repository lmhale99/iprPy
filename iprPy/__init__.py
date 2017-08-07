"""
Attributes
----------
rootdir : str
    The absolute path to the iprPy package's root directory used to locate
    contained data files.
"""
from __future__ import division, absolute_import, print_function

import os

# Read version from VERSION file
with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

__all__ = ['__version__', 'rootdir', 'tools', 'calculations', 'records',
           'databases', 'prepare', 'input', 'highthroughput', 'check_modules']

# Define root package directory
rootdir = os.path.dirname(os.path.abspath(__file__))
    
# Basic submodule imports
from . import tools

# Modular submodule imports
from . import calculations
from . import calculation_functions
from .calculation_functions import *
from . import records
from . import record_functions
from .record_functions import *
from . import databases
from . import database_functions
from .database_functions import *

from .check_modules import check_modules
from . import prepare
from . import input
from . import highthroughput

__all__.extend(calculation_functions.__all__)
__all__.extend(record_functions.__all__)
__all__.extend(database_functions.__all__)
__all__.sort()

