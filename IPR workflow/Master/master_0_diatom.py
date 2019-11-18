from copy import deepcopy
from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

from iprPy.tools import aslist

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_1'
    num_runners = 1
    np_per_runner = 1
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

    # Set other generic settings
    #global_kwargs['prototype_id'] = 'A1--Cu--fcc'

    # Potential-based modifiers
    pot_kwargs = {}
    #pot_kwargs['id'] = ['2015--Thompson-A-P--Ta--LAMMPS--ipr2']
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Initialize pool of workers
    if num_runners > 1:
        pool = Pool(num_runners)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    # Prepare diatom_scan
    kwargs = deepcopy(global_kwargs)
    for key in pot_kwargs:
        kwargs[f'potential_{key}'] = pot_kwargs[key]

    #try:
    #    prepare.diatom_scan.bop(database_name, run_directory_name, **kwargs)
    #except:
    #    pass        
    
    prepare.diatom_scan.main(database_name, run_directory_name, **kwargs)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! # 

    # Run diatom_scan
    multi_runners(database_name, run_directory_name, num_runners, pool=pool)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Close pool
    if pool is not None:
        pool.close()