# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'point_defect_static'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares point_defect_static calculations from relaxed_crystal
    records. The elastic constants are computed for four different sizemults.

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

        # Build defect records
        'buildcombos                 defect pointdefect_file',
        'defect_record               point_defect',

        # System manipulations
        'sizemults                   6 6 6',
        'sizemults                   8 8 8',
        'sizemults                   10 10 10',
        'sizemults                   12 12 12',

        # Run parameters
        'energytolerance             ',
        'forcetolerance              1e-8',
        'maxiterations               ',
        'maxevaluations              ',
        'maxatommotion               ',
        ])
    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    
    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)