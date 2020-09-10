# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'dislocation_periodic_array'

def fcc_edge_mix(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_periodic_array calculations from elastic_constants_static
    records for fcc dislocations with edge components.

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
        'parent_family               A1--Cu--fcc',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',
        'defect_id                   A1--Cu--fcc--a-2-110--90-edge--{111}',

        # System manipulations
        'sizemults                   1 200 50',

        # Run parameters
        'dislocation_boundarywidth   3',
        'dislocation_boundaryscale   True',
        'dislocation_duplicatecutoff 1 angstrom',
        'dislocation_onlylinear      False',
        'annealtemperature           10',
        'annealsteps                 10000',
        'randomseed                  ',
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


def fcc_screw(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_periodic_array calculations from elastic_constants_static
    records.  Same as fcc_edge_mix, except uselinear is set to True and defect is
    limited to only pure screw dislocations.

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
        'parent_family               A1--Cu--fcc',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',
        'defect_id                   A1--Cu--fcc--a-2-110--0-screw--{111}',

        # System manipulations
        'sizemults                   1 200 50',

        # Run parameters
        'dislocation_boundarywidth   3',
        'dislocation_boundaryscale   True',
        'dislocation_duplicatecutoff 1 angstrom',
        'dislocation_onlylinear      True',
        'annealtemperature           10',
        'annealsteps                 10000',
        'randomseed                  ',
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