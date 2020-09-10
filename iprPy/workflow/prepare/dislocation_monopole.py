# Standard Python libraries
import sys

# iprPy imports
from . import prepare

calculation_name = 'dislocation_monopole'

def fcc_edge_100(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_monopole calculations from elastic_constants_static
    records.  The sizemults are specifically selected for 
    A1--Cu--fcc--a-2-110--90-edge--{100} dislocations.

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
        'defect_id                   A1--Cu--fcc--a-2-110--90-edge--{100}',

        # System manipulations
        'sizemults                   1 80 116',

        # Run parameters
        'dislocation_boundarywidth   ',
        'dislocation_boundaryshape   ',
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

def bcc_screw(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_monopole calculations from elastic_constants_static
    records.  The sizemults are specifically selected for 
    A2--W--bcc--a-2-111--0-screw--{110} dislocations.

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
        'parent_family               A2--W--bcc',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',
        'defect_id                   A2--W--bcc--a-2-111--0-screw--{110}',

        # System manipulations
        'sizemults                   1 48 80',

        # Run parameters
        'dislocation_boundarywidth   3',
        'dislocation_boundaryscale   True',
        'dislocation_boundaryshape   cylinder',
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

def bcc_edge(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_monopole calculations from elastic_constants_static
    records.  The sizemults are specifically selected for 
    A2--W--bcc--a-2-111--90-edge--{110} dislocations.

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
        'parent_family               A2--W--bcc',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',
        'defect_id                   A2--W--bcc--a-2-111--90-edge--{110}',

        # System manipulations
        'sizemults                   1 68 80',

        # Run parameters
        'dislocation_boundarywidth   ',
        'dislocation_boundaryshape   ',
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

def bcc_edge_112(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares dislocation_monopole calculations from elastic_constants_static
    records.  The sizemults are specifically selected for 
    A2--W--bcc--a-2-111--90-edge--{112} dislocations.

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
        'parent_family               A2--W--bcc',

        # Build defect records
        'buildcombos                 defect dislocation_file',
        'defect_record               dislocation',
        'defect_id                   A2--W--bcc--a-2-111--90-edge--{112}',

        # System manipulations
        'sizemults                   1 68 48',

        # Run parameters
        'dislocation_boundarywidth   ',
        'dislocation_boundaryshape   ',
        'annealtemperature           10',
        'annealsteps                 10000',
        'randomseed                  ',
        'energytolerance             ',
        'forcetolerance              ',
        'maxiterations               10000',
        'maxevaluations              100000',
        'maxatommotion               ',
        ])        

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)