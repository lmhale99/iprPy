# coding: utf-8

# Standard Python libraries
from datetime import date

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

def test_lammps_versions(commands):
    """
    Tests the primary and alternative lammps commands listed in the loaded 
    commands file.  Only works when called on the machine where the executables
    are accessible, i.e. don't use if preparing on a different resource!
    Issues an error if the primary lammps command is inaccessible or too old.
    Ignores alternate lammps commands if they are inaccessible or not in the
    required date range.
    
    lammps_command - must be 30 Oct 2019 or newer.
    lammps_command_snap_1 - must be between 8 Aug 2014 and 30 May 2017.
    lammps_command_snap_2 - must be between 3 Dec 2018 and 12 Jun 2019.
    lammps_command_old - must be before 30 Oct 2019.

    Parameters
    ----------
    commands : dict
        The mpi and lammps commands to use when preparing.
    """
    
    # Test main LAMMPS command
    lammps_command = commands['lammps_command']
    lammpsdate = lmp.checkversion(lammps_command)['date']
    assert lammpsdate >= date(2019, 10, 30)

    # Define test for older LAMMPS commands
    def test_old(commands, key, startdate=None, enddate=None):
        if key in commands:
            command = commands[key]
        else:
            return True

        try:
            lammpsdate = lmp.checkversion(command)['date']
        except:
            print(f'{key} not found or not working')
        else:
            if startdate is not None and lammpsdate < startdate:
                print(f'{key} too old')
            elif enddate is not None and lammpsdate > enddate:
                print(f'{key} too new')
            else:
                return True
        return False

    # Test older LAMMPS commands
    if not test_old(commands, 'lammps_command_snap_1', date(2014,  8,  8), date(2017,  5, 30)):
        del commands['lammps_command_snap_1']
    if not test_old(commands, 'lammps_command_snap_2', date(2018, 12,  3), date(2019,  6, 12)):
        del commands['lammps_command_snap_2']
    if not test_old(commands, 'lammps_command_old', None, date(2019, 10, 30)):   
        del commands['lammps_command_old']