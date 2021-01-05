# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'E_vs_r_scan'

def main(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares E_vs_r_scan calculations from crystal_prototype records.

    buildcombos
    - prototype : crystalprototype from crystal_prototype

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
        # Build load information based on prototype records
        'buildcombos                 crystalprototype load_file prototype',   

        # System manipulations
        'sizemults                   10 10 10',

        # Run parameters
        'minimum_r                   0.5',
        'maximum_r                   6.0',
        'number_of_steps_r           276', 
        ]) 
    
    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            kwargs[f'prototype_potential_{key}'] = pot_kwargs[key]

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)

def bop(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares E_vs_r_scan calculations from crystal_prototype records for 
    pair_style bop potentials.  A larger minimum_r value is used for bop 
    potentials as bop have large cutoff distances resulting in extremely large
    neighbor lists.

    buildcombos
    - prototype : crystalprototype from crystal_prototype

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
        # Build load information based on prototype records
        'buildcombos                 crystalprototype load_file prototype',
        
        # Specify prototype buildcombos limiters (only build for potential listed)
        'prototype_potential_pair_style  bop',
        
        # System manipulations
        'sizemults                   10 10 10',
        
        # Run parameters
        'minimum_r                   2.0',
        'maximum_r                   6.0',
        'number_of_steps_r           201',
        ]) 

    # Add pot_kwargs with the appropriate prefix
    if pot_kwargs is not None:
        for key in pot_kwargs:
            if key != 'pair_style':
                kwargs[f'prototype_potential_{key}'] = pot_kwargs[key]

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)

