# Standard Python libraries
import sys

# iprPy imports
from . import prepare
from ... import load_database

calculation_name = 'isolated_atom'

def main(database_name, run_directory_name, lammps_command, **kwargs):
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
    lammps_command : str
        The LAMMPS executable to use.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """

    # Set default branch value to match current function's name
    kwargs['branch'] = kwargs.get('branch', sys._getframe().f_code.co_name)

    script = "\n".join(
        [
        # Build load information based on potential records
        'buildcombos                 interatomicpotential potential_file intpot',   
        ]) 
    
    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)
