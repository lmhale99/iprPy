from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'test'
    run_directory_name = 'test_1'
    np = 4

    # Lammps and mpi commands
    lammps_command = 'lmp_serial'
    #mpi_command = f'c:\\Program Files\\MPICH2\\bin\\mpiexec -localonly {np}' # local
    #mpi_command = f'mpirun -np {np}' # cluster
    
    # Potential-based modifiers
    pot_kwargs = {}
    pot_kwargs['id'] = '1999--Mishin-Y--Al--LAMMPS--ipr1'
    #pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Prototype-based modifiers
    family = 'A1--Cu--fcc'
    #family = None

    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare relax_dynamic at temperature
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    #kwargs['mpi_command'] = mpi_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family

    prepare.relax_dynamic.at_temp(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare phonon
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family

    prepare.phonon.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run big sims
    #multi_runners(database_name, run_directory_name, 1)
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare elastic_constants_static
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family

    prepare.elastic_constants_static.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare surface_energy_static
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family
        kwargs['defect_family'] = family

    prepare.surface_energy_static.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare point_defect_static
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family
        kwargs['defect_family'] = family

    prepare.point_defect_static.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare stacking_fault_map_2D
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family
        kwargs['defect_family'] = family
        
    prepare.stacking_fault_map_2D.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run small sims
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()