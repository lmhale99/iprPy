# Define rootdir
import os
rootdir = os.path.dirname(os.path.abspath(__file__))

# Read version from VERSION file
with open(os.path.join(rootdir, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

# Basic submodule imports
from . import tools 

# Modular submodule imports
from . import calculations
from .calculation_functions import *

from . import records
from .record_functions import *

from . import databases
from .database_functions import *

# Import check_modules function
from .check_modules import check_modules

from . import prepare
from . import input

from . import highthroughput
