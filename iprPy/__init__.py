# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
__version__ = resources.read_text('iprPy', 'VERSION').strip()

__all__ = ['__version__', 'tools', 'Settings', 'input', 'Library',
           'record', 'load_record', 
           'calculation', 'load_calculation',
           'database', 'load_database', 
           'analysis', 'workflow', 'check_modules', 'command_line']
__all__.sort()

# iprPy imports
from . import tools

from .settings import Settings, load_run_directory

from . import analysis
from . import input

from . import record
from .record import load_record

from .library import Library

from . import calculation
from .calculation import load_calculation

from . import database
from .database import load_database

from . import workflow

from .check_modules import check_modules

from .command_line import command_line