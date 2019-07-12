from . import prepare

calculation_name = 'relax_box'

def main(database_name, run_directory_name, lammps_command, **kwargs):
    """
    Prepares relax_box calculations from reference_crystal and E_vs_r_scan
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
    lammps_command : str
        The LAMMPS executable to use.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    
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
        'strainrange                 1e-6',
        ])

    # Add additional required terms to kwargs
    kwargs['lammps_command'] = lammps_command

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
                 script, **kwargs)