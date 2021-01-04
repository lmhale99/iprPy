# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'relax_static'

def main(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares relax_static calculations from reference_crystal and E_vs_r_scan
    records.

    buildcombos
    - reference : atomicreference from reference_crystal
    - parent : atomicparent from calculation_E_vs_r_scan

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
        # Build load information based on reference structures
        'buildcombos                 atomicreference load_file reference',

        # Build load information from E_vs_r_scan results
        'buildcombos                 atomicparent load_file parent',

        # Specify parent buildcombos terms (parent record's style and the load_key to access)
        'parent_record               calculation_E_vs_r_scan',          
        'parent_load_key             minimum-atomic-system',
        'parent_status               finished',

        # System manipulations
        'sizemults                   10 10 10',

        # Run parameters
        'energytolerance             0.0',
        'forcetolerance              1e-10 eV/angstrom',
        'maxiterations               10000',
        'maxevaluations              100000',
        'maxatommotion               0.01 angstrom',
        'maxcycles                   100',
        'cycletolerance              1e-10',
        ])

    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            kwargs[f'reference_potential_{key}'] = pot_kwargs[key] 
            kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)

def from_dynamic(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares relax_static calculations from relax_dynamic records.

    buildcombos
    - archive : atomicarchive from calculation_relax_dynamic

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
        # Build load information from relax_dynamic results
        'buildcombos                 atomicarchive load_file archive',

        # Specify archive parent buildcombos terms (parent record's style and the load_key to access)
        'archive_record              calculation_relax_dynamic',
        'archive_branch              main',
        'archive_load_key            final-system',
        'archive_status              finished',

        # System manipulations             
        'sizemults                   1 1 1',

        # Run parameters
        'energytolerance             0.0',
        'forcetolerance              1e-10 eV/angstrom',
        'maxiterations               10000',
        'maxevaluations              100000',
        'maxatommotion               0.01 angstrom',
        'maxcycles                   100',
        'cycletolerance              1e-10',
        ])

    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            kwargs[f'archive_potential_{key}'] = pot_kwargs[key]
    
    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)