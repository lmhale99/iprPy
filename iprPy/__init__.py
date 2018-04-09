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

__all__ = ['__version__', 'rootdir', 'tools', 'calculations', 'records',
           'databases', 'prepare', 'input', 'highthroughput', 'check_modules']

# Define root package directory
rootdir = os.path.dirname(os.path.abspath(__file__))

# iprPy imports
from . import compatibility
from . import tools

from . import calculations
from .calculation_functions import *
from .calculation_functions import __all__ as calculation_functions_all
__all__.extend(calculation_functions_all)

from . import records
from .record_functions import *
from .record_functions import __all__ as record_functions_all
__all__.extend(record_functions_all)

from . import databases
from .database_functions import *
from .database_functions import __all__ as database_functions_all
__all__.extend(database_functions_all)

from .check_modules import check_modules
from . import prepare
from . import input
from . import highthroughput
__all__.sort()