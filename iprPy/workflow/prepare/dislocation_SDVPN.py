# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'dislocation_SDVPN'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_SDVPN calculations from elastic_constants_static
    and stacking_fault_map_2D records.

    buildcombos
    - parent : atomicarchive from elastic_constants_static
    - defect : defect from dislocation

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
        'buildcombos                 atomicarchive load_file parent',
        'parent_record               calculation_elastic_constants_static',
        'parent_load_key             system-info',
        'parent_strainrange          1e-7',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',

        # Run parameters
        ])        

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)