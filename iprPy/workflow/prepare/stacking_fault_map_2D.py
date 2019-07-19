# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'stacking_fault_map_2D'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares stacking_fault_map_2D calculations from relaxed_crystal
    records.

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
        'parent_method               dynamic',

        # Build defect records
        'buildcombos                 defect stackingfault_file',
        'defect_record               stacking_fault',

        # System manipulations
        'sizemults                   5 5 10',

        # Run parameters
        'stackingfault_numshifts1    30',
        'stackingfault_numshifts2    30',
        'energytolerance             ',
        'forcetolerance              ',
        'maxiterations               ',
        'maxevaluations              ',
        'maxatommotion               ',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)