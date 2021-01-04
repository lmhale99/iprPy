# Standard Python libraries
import sys
from copy import deepcopy

# iprPy imports
from . import prepare
from ... import load_database

calculation_name = 'isolated_atom'

def main(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares diatom_scan calculations for potentials.

    buildcombos
    - None, custom code here

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
        # Build load information based on potential records
        'buildcombos                 interatomicpotential potential_file intpot',   
        ])

    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            kwargs[f'intpot_{key}'] = pot_kwargs[key]

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
            script, **kwargs)
