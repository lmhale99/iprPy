from copy import deepcopy
from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_3'
    num_runners = 1
    np_per_runner = 4
    run_location = 'local'

    # Generic settings
    global_kwargs = {}
    
    # Set commands for this computer
    if run_location == 'local':
        global_kwargs['lammps_command'] = 'lmp_mpi'
        if np_per_runner > 1:
            global_kwargs['mpi_command'] = f'c:\\Program Files\\MPICH2\\bin\\mpiexec -localonly {np_per_runner}' 
    
    # Set commands for ruth cluster
    elif run_location == 'ruth':
        assert num_runners == 0, 'num_runners must be 0 if run_location is not "local"'
        global_kwargs['lammps_command'] = 'lmp_mpi'
        if np_per_runner > 1:
            global_kwargs['mpi_command'] = f'/cluster/deb9/bin/mpirun -n {np_per_runner}' 
    
    #global_kwargs['parent_standing'] = 'good'

    # Potential-based modifiers
    pot_kwargs = {}
    #pot_kwargs['id'] = ['2003--Mendelev-M-I--Fe-2--LAMMPS--ipr3']
    pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Initialize pool of workers
    if num_runners > 1:
        pool = Pool(num_runners)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Prepare 
    kwargs = deepcopy(global_kwargs)
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    prepare.dislocation_monopole.bcc_screw(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.bcc_edge(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.bcc_edge_112(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_edge(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_edge_100(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_screw(database_name, run_directory_name, **kwargs)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    # Run 
    multi_runners(database_name, run_directory_name, num_runners, pool=pool)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Close pool
    if pool is not None:
        pool.close()    