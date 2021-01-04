# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'surface_energy_static'

def main(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares surface_energy_static calculations from relaxed_crystal
    records.

    buildcombos
    - parent : atomicparent from relaxed_crystal

    Parameters
    ----------
    database_name : str
        The name of the pre-set database to use.
    run_directory_name : str
        The name of the pre-set run_directory to use.
    pot_kwargs : dict, optional
        Values for potential-specific limiters.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    # Check for required kwargs
    assert 'lammps_command' in kwargs

    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    # Define script with default parameter values
    script = "\n".join(
        [
        # Build load information from dynamic relaxed_crystal
        'buildcombos                 atomicparent load_file parent',
        'parent_record               relaxed_crystal',
        'parent_method               dynamic',
        'parent_standing             good',

        # Build defect records
        'buildcombos                 defect surface_file',
        'defect_record               free_surface',

        # System manipulations
        'sizemults                   3 3 8',
                    

        # Run parameters
        'energytolerance             ',
        'forcetolerance              ',
        'maxiterations               ',
        'maxevaluations              ',
        'maxatommotion               ',    
        ])

    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)