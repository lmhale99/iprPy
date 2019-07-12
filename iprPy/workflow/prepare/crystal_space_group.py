from . import prepare

calculation_name = 'crystal_space_group'

def relax(database_name, run_directory_name, **kwargs):
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
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    
    script = "\n".join(
        [
        # Build load information from relax_static results
        "buildcombos                 atomicarchive load_file relax_static",
        
        # Specify archive parent buildcombos terms (parent record's style and the load_key to access)
        "relax_static_record         calculation_relax_static",
        "relax_static_load_key       final-system",
        
        # Build load information from relax_box results
        "buildcombos                 atomicarchive load_file relax_box",
        
        # Specify archive parent buildcombos terms (parent record's style and the load_key to access)
        "relax_box_record            calculation_relax_box",
        "relax_box_load_key          final-system",
        
        # Run parameters
        "symmetryprecision           ",       
        "primitivecell               ",  
        "idealcell                   ",
        ])

    # Prepare 
    prepare(database_name, run_directory_name, calculation_name,
            script, **kwargs)

def protoref(database_name, run_directory_name, **kwargs):
    """
    Prepares crystal_space_group calculations from crystal_prototype and
    reference_crystal records.

    buildcombos
    - proto : crystalprototype from crystal_prototype
    - ref : atomicreference from reference_crystal

    Parameters
    ----------
    database_name : str
        The name of the pre-set database to use.
    run_directory_name : str
        The name of the pre-set run_directory to use.
    **kwargs : str or list, optional
        Values for any additional or replacement prepare parameters. 
    """
    
    script = "\n".join(
        [
        # Build load information based on prototype records
        "buildcombos                 crystalprototype load_file proto",
        
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