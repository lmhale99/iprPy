# coding: utf-8
# Standard Python libraries
from importlib import resources

# Read version from VERSION file
__version__ = resources.read_text('iprPy', 'VERSION').strip()

__all__ = ['__version__', 'tools', 'settings', 'input', 
           'load_run_directory', 'fix_lammps_versions',
           'record', 'load_record', 'recordmanager',
           'calculation_subset',
           'calculation', 'load_calculation', 'calculationmanager',
           'database', 'load_database', 'databasemanager',
           'check_modules', 'command_line']
__all__.sort()

# iprPy imports
from . import tools

from .Settings import settings
from .load_run_directory import load_run_directory
from .fix_lammps_versions import fix_lammps_versions

#from . import analysis
from . import input

from . import record
from .record import load_record, recordmanager

#from .library import Library
from . import calculation_subset
from . import calculation
from .calculation import load_calculation, calculationmanager

from .database import load_database, databasemanager

from .check_modules import check_modules

from .command_line import command_line