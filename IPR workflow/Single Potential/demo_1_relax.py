from pathlib import Path

from multiprocessing import Pool

from multi_runners import multi_runners
import workflow_prepare as prepare
from process_relax import process_relax 

from iprPy.tools import aslist

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'demo'
    run_directory_name = 'master_2'
    np = 4

    # Lammps and mpi commands
    lammps_command = 'lmp_mpi'
    mpi_command = f'c:\\Program Files\\MPICH2\\bin\\mpiexec -localonly {np}' # Used for big/long sims
    
    # Potential-based modifiers
    pot_kwargs = {}
    pot_kwargs['id'] = '1999--Mishin-Y--Ni--LAMMPS--ipr1'
    #pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Prototype-based modifiers
    family = 'A1--Cu--fcc'
    #family = None

    # Paths to compiled results
    crystal_match_file = Path('reference_prototype_match.csv')
    all_crystals_file = Path(f'{database_name}_all_crystals.csv')
    unique_crystals_file = Path(f'{database_name}_unique_crystals.csv')



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare E_vs_r_scan
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'prototype_potential_{key}'] = pot_kwargs[key]
    
    if family is not None:
        kwargs[f'prototype_id'] = family

    if 'pair_style' not in pot_kwargs:
        prepare.E_vs_r_scan.bop(database_name, run_directory_name, **kwargs)
        prepare.E_vs_r_scan.main(database_name, run_directory_name, **kwargs)
    else:
        if 'bop' in aslist(pot_kwargs['pair_style']):
            pair_style = kwargs.pop('prototype_potential_pair_style')
            prepare.E_vs_r_scan.bop(database_name, run_directory_name, **kwargs)
            kwargs['prototype_potential_pair_style'] = pair_style
        prepare.E_vs_r_scan.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! # 
    # Run E_vs_r_scan
    multi_runners(database_name, run_directory_name, np, pool=pool)   
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare relax_dynamic at 0 K
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    kwargs['mpi_command'] = mpi_command
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key]   
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    
    if family is not None:
        kwargs[f'parent_family'] = family

    prepare.relax_dynamic.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #        
    # Run relax_dynamic
    multi_runners(database_name, run_directory_name, 1)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare relax_box
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key]   
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    if family is not None:
        kwargs[f'parent_family'] = family

    prepare.relax_box.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare relax_static
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key]   
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    
    if family is not None:
        kwargs[f'parent_family'] = family

    prepare.relax_static.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare relax_static from relax_dynamic
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'archive_potential_{key}'] = pot_kwargs[key]

    if family is not None:
        kwargs[f'archive_family'] = family

    prepare.relax_static.from_dynamic(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run relax_static and relax_box
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare crystal_space_group
    kwargs = {}
    kwargs['lammps_command'] = lammps_command

    prepare.crystal_space_group.relax(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run crystal_space_group
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Close pool
    if pool is not None:
        pool.close()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Call process relaxation results and generate relaxed_crystal records
    process_relax(database_name, crystal_match_file, all_crystals_file, unique_crystals_file)