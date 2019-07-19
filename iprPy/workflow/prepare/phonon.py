# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'phonon'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares phonon calculations from relaxed_crystal records.

    buildcombos
    - parent : atomicparent from relaxed_crystal

    Parameters
    ----------
    database_name : str
        The name of the pre-set database to use.
    run_directory_name : str
        The name of the pre-set run_directory to use.
    lammps_command : str
        The LAMMPS executable to use.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    script = "\n".join(
        [
        # Build load information from dynamic relaxed_crystal
        'buildcombos                 atomicparent load_file parent',
        'parent_record               relaxed_crystal',

        # System manipulations
        'sizemults                   5 5 5',

        # Run parameters
        'displacementdistance        ',
        'symmetryprecision           ',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)