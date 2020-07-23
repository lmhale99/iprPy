# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'elastic_constants_static'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares elastic_constants_static calculations from relaxed_crystal
    records. The elastic constants are computed for four different strain
    ranges: 1e-5, 1e-6, 1e-7, and 1e-8.

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
        # Build load information from crystal_space_group results
        'buildcombos                 atomicparent load_file parent',
        'parent_record               relaxed_crystal',

        # System manipulations
        'sizemults                   10 10 10',

        # Run parameters
        'energytolerance             ',
        'forcetolerance              ',
        'maxiterations               5000',
        'maxevaluations              10000',
        'maxatommotion               ',
        'strainrange                 1e-6',
        'strainrange                 1e-7',
        'strainrange                 1e-8',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)