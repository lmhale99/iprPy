# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'crystal_space_group'

def relax(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares crystal_space_group calculations from relax_static and
    relax_box calculation results.

    buildcombos
    - relax_static : atomicarchive from calculation_relax_static
    - relax_box : atomicarchive from calculation_relax_box

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
    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    # Define script with default parameter values
    script = "\n".join(
        [
        # Build load information from relax_static results
        "buildcombos                 atomicarchive load_file archive1",
        
        # Specify archive parent buildcombos terms (parent record's style and the load_key to access)
        "archive1_record             calculation_relax_static",
        "archive1_load_key           final-system",
        "archive1_status             finished",
        
        # Build load information from relax_box results
        "buildcombos                 atomicarchive load_file archive2",
        
        # Specify archive parent buildcombos terms (parent record's style and the load_key to access)
        "archive2_record             calculation_relax_box",
        "archive2_load_key           final-system",
        "archive2_status             finished",
        
        # Run parameters
        "symmetryprecision           ",       
        "primitivecell               ",  
        "idealcell                   ",
        ])

    # Add the recognized pot_kwargs
    if pot_kwargs is not None:
        if 'id' in pot_kwargs:
            kwargs[f'archive1_potential_LAMMPS_id'] = pot_kwargs['id']
            kwargs[f'archive2_potential_LAMMPS_id'] = pot_kwargs['id']
        if 'key' in pot_kwargs:
            kwargs[f'archive1_potential_LAMMPS_key'] = pot_kwargs['key']
            kwargs[f'archive2_potential_LAMMPS_key'] = pot_kwargs['key']
        if 'pot_id' in pot_kwargs:
            kwargs[f'archive1_potential_id'] = pot_kwargs['pot_id']
            kwargs[f'archive2_potential_id'] = pot_kwargs['pot_id']
        if 'pot_key' in pot_kwargs:
            kwargs[f'archive1_potential_key'] = pot_kwargs['pot_key']
            kwargs[f'archive2_potential_key'] = pot_kwargs['kepot_keyy']

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
            script, **kwargs)

def prototype(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares crystal_space_group calculations from crystal_prototype records.

    buildcombos
    - proto : crystalprototype from crystal_prototype

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
    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    # Define script with default parameter values
    script = "\n".join(
        [
        # Build load information based on prototype records
        "buildcombos                 crystalprototype load_file proto",
        
        # Run parameters
        "symmetryprecision           ",
        "primitivecell               ",
        "idealcell                   ",
        ])

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)

def reference(database_name, run_directory_name, pot_kwargs=None, **kwargs):
    """
    Prepares crystal_space_group calculations from reference_crystal records.

    buildcombos
    - ref : atomicreference from reference_crystal

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
    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    # Define script with default parameter values
    script = "\n".join(
        [
        # Build load information based on reference structures
        "buildcombos                 atomicreference load_file ref",
        
        # Run parameters
        "symmetryprecision           ",
        "primitivecell               ",
        "idealcell                   ",
        ])

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)