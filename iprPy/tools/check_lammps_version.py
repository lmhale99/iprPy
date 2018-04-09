# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

def check_lammps_version(lammps_command):
    """
    Gets the LAMMPS version and date information by testing lammps_command.
    
    Parameters
    ----------
    lammps_command: str
        The LAMMPS executable to get the version for.
        
    Returns
    -------
    version_info: dict
        Dictionary containing 'lammps_version', the str LAMMPS version, and
        'lammps_date', the corresponding  datetime.date for the LAMMPS 
        version.
        
    Raises
    ------
    ValueError
        If lammps fails to run
    """
    # Define absolute path to emptyscript
    emptyscript = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'empty.in')
    logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'empty.lammps')
    
    # Create emptyscript if it doesn't exist
    if not os.path.isfile(emptyscript):
        with open(emptyscript, 'w') as f:
            f.write('')
    
    # Run lammps_command with emptyscript
    try:
        log = lmp.run(lammps_command, emptyscript, logfile=logfile)
    except:
        raise ValueError('Failed to run simulation with lammps_command '+lammps_command)
    
    # Extract lammps version and date info
    version_info = {}
    version_info['lammps_version'] = log.lammps_version
    version_info['lammps_date'] = log.lammps_date
    return version_info