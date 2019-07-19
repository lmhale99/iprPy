from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'test'
    run_directory_name = 'test_1'
    np = 3

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
    # Prepare dislocation_monopole
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    #kwargs['mpi_command'] = mpi_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family

    prepare.dislocation_monopole.fcc_screw(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_edge(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_edge_100(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare dislocation_monopole
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    #kwargs['mpi_command'] = mpi_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    if family is not None:
        kwargs['parent_family'] = family

    prepare.dislocation_periodic_array.screw(database_name, run_directory_name, **kwargs)
    prepare.dislocation_periodic_array.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run big sims
    #multi_runners(database_name, run_directory_name, 1)
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()