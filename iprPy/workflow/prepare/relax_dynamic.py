# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'relax_dynamic'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares relax_dynamic calculations from reference_crystal and E_vs_r_scan
    records for 0K and 0 pressure relaxations.

    buildcombos
    - reference : atomicreference from reference_crystal
    - parent : atomicparent from calculation_E_vs_r_scan

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
        # Build load information based on reference structures
        'buildcombos                 atomicreference load_file reference',

        # Build load information from E_vs_r_scan results
        'buildcombos                 atomicparent load_file parent',

        # Specify parent buildcombos terms (parent record's style and the load_key to access)
        'parent_record               calculation_E_vs_r_scan',         
        'parent_load_key             minimum-atomic-system',

        # System manipulations
        'sizemults                   10 10 10',

        # Run parameters
        'temperature                 0.0',
        'pressure_xx                 ',
        'pressure_yy                 ',
        'pressure_zz                 ',
        'pressure_xy                 ',
        'pressure_xz                 ',
        'pressure_yz                 ',
        'integrator                  nph+l',
        'thermosteps                 1000',
        'dumpsteps                   ',
        'runsteps                    10000',
        'equilsteps                  0',
        'randomseed                  ',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)

def at_temp(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares relax_dynamic calculations from relaxed_crystal records for every 100K
    up to 3000K, and 0 pressure.

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

        # System manipulations  
        'sizemults                   10 10 10',

        # Run parameters
        'temperature                 100',
        'temperature                 200',
        'temperature                 300',
        'temperature                 400',
        'temperature                 500',
        'temperature                 600',
        'temperature                 700',
        'temperature                 800',
        'temperature                 900',
        'temperature                 1000',
        'temperature                 1100',
        'temperature                 1200',
        'temperature                 1300',
        'temperature                 1400',
        'temperature                 1500',
        'temperature                 1600',
        'temperature                 1700',
        'temperature                 1800',
        'temperature                 1900',
        'temperature                 2000',
        'temperature                 2100',
        'temperature                 2200',
        'temperature                 2300',
        'temperature                 2400',
        'temperature                 2500',
        'temperature                 2600',
        'temperature                 2700',
        'temperature                 2800',
        'temperature                 2900',
        'temperature                 3000',
        'pressure_xx                 0.0',
        'pressure_yy                 0.0',
        'pressure_zz                 0.0',
        'pressure_xy                 0.0',
        'pressure_xz                 0.0',
        'pressure_yz                 0.0',
        'integrator                  npt',
        'thermosteps                 100',
        'dumpsteps                   ',
        'runsteps                    22000',
        'equilsteps                  2000',
        'randomseed                  ',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command
    
    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)