# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import shutil
import tempfile

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

__all__ = ['lammps_commands']

def lammps_commands(input_dict, **kwargs):
    """
    Interprets calculation parameters associated with lammps_command and
    mpi_command input_dict keys.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    
    - **'lammps_command'** the LAMMPS command to use for running simulations.
    - **'mpi_command'** the specific MPI command to run LAMMPS in parallel.
    - **'lammps_version'** the version of LAMMPS associated with
      lammps_command.
    - **'lammps_date'** a datetime.date object of the LAMMPS version.
       
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    lammps_command : str
        Replacement parameter key name for 'lammps_command'.
    mpi_command : str
        Replacement parameter key name for 'mpi_command'.
    lammps_version : str
        Replacement parameter key name for 'lammps_version'.
    lammps_date : str
        Replacement parameter key name for 'lammps_date'.
    """
    
    # Set default keynames
    keynames = ['lammps_command', 'mpi_command', 'lammps_version',
                'lammps_date']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    # Extract input values and assign default values
    lammps_command = input_dict[kwargs['lammps_command']]
    mpi_command = input_dict.get(kwargs['mpi_command'], None)
    
    # Retrieve lammps_version info
    lammps_version = lmp.checkversion(lammps_command)
    
    # Save processed terms
    input_dict[kwargs['mpi_command']] = mpi_command
    input_dict[kwargs['lammps_version']] = lammps_version['version']
    input_dict[kwargs['lammps_date']] = lammps_version['date']