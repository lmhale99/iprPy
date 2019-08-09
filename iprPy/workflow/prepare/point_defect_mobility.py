# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'point_defect_mobility'

def main(database_name, run_directory_name, lammps_command, mpi_command, **kwargs):
    """
    Prepares point_defect_mobility calculations from relaxed_crystal
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

        # Build defect mobility records - note that this also builds load information from dynamic relaxed_crystal
        'buildcombos                 defectmobility pointdefect_mobility_file',
        'defectmobility_record               point_defect_mobility',

        # System manipulations - note that the -1 setting is used because the 
        # system manipulate seems to be generating systems oddly, and may be
        # removed in the future if that issue gets fixed.
        # Also, point defect mobility calculations are much slower than static
        # point defect calculations, so it may not be feasable to run as many copies of sizemults.
        'sizemults                   -1 6 -1 6 -1 6',

        # Run parameters
        'energytolerance             ',
        'forcetolerance              1e-6',
        'maxiterations               ',
        'maxevaluations              ',
        'maxatommotion               ',
        ])
    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command
    kwargs['mpi_command'] = mpi_command
    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)