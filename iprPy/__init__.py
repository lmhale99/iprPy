# coding: utf-8

# Standard Python libraries
from importlib import resources

# Read version from VERSION file
if hasattr(resources, 'files'):
    __version__ = resources.files('iprPy').joinpath('VERSION').read_text(encoding='UTF-8').strip()
else:
    __version__ = resources.read_text('iprPy', 'VERSION', encoding='UTF-8').strip()

# iprPy imports
from . import tools
from .Settings import settings
from .load_run_directory import load_run_directory
from .fix_lammps_versions import fix_lammps_versions
from . import input

from . import value
from .value import valuemanager
from . import record
from .record import load_record, recordmanager

from . import calculation_subset
from . import calculation
from .calculation import load_calculation, calculationmanager

from .database import load_database, databasemanager, reset_orphans

from .check_modules import check_modules
from .command_line import command_line

from . import analysis

from . import quickcheck

__all__ = ['__version__', 'tools', 'settings', 'input',
           'load_run_directory', 'fix_lammps_versions',
           'record', 'load_record', 'recordmanager',
           'calculation_subset', 'analysis',
           'calculation', 'load_calculation', 'calculationmanager',
           'database', 'load_database', 'databasemanager',
           'check_modules', 'command_line', 'reset_orphans', 'quickcheck']
__all__.sort()
