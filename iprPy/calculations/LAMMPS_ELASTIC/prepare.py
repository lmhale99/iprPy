import os
import shutil
import sys
import glob
import uuid

from DataModelDict import DataModelDict as DM
import atomman.lammps as lmp

from iprPy.tools import fill_template, atomman_input, term_extractor
from .data_model import data_model
from .read_input import read_input

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__)) 
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def description():
    """Returns a description for the calculation."""
    return "The refine_structure_static calculation uses molecular statics to find the equilibrium box size and elastic constants of a system using a specific potential and at a specific pressure."
    
def keywords():
    """Return the list of keywords used by this calculation that are searched for from the inline inline_terms and pre-defined global_variables."""
    return ['run_directory',
            'lib_directory',
            'copy_files',
            'lammps_command',
            'mpi_command',
            'potential_file',
            'potential_dir',
            'load',
            'load_options',
            'load_elements',
            'box_parameters',
            'size_mults',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'strain_range',
            'pressure_xx',
            'pressure_yy',
            'pressure_zz']

def singular_keywords():
    """Returns a dictionary of keywords that should have only one value for the calculation's prepare function, and the default values.""" 
    return {'run_directory':       None,
            'lib_directory':       None,
            'copy_files':          'true',
            'lammps_command':      None,
            'mpi_command':         '',
            'length_unit':         '',
            'pressure_unit':       '',
            'energy_unit':         '',
            'force_unit':          '',
            'strain_range':        '',
            'pressure_xx':         '',
            'pressure_yy':         '',
            'pressure_zz':         ''}

def unused_keywords():
    """Returns a list of the keywords in the calculation's template input file that the prepare function does not use."""
    return ['x-axis', 
            'y-axis', 
            'z-axis', 
            'shift']

def prepare(inline_terms, global_variables):
    """This is the prepare method for the calculation"""
    
    raise ValueError("This calculation doesn't have a prepare function!")