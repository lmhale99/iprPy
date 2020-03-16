from copy import deepcopy
from pathlib import Path

from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

from iprPy.tools import aslist

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_4'
    num_runners = 0
    np_per_runner = 6
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
    global_kwargs['parent_family'] = 'A3--Mg--hcp'
    #global_kwargs['reference_'] = 
    
    # Potential-based modifiers
    pot_kwargs = {}
    pot_kwargs['id'] = [
        #'2014--Liyanage-L-S-I--Fe-C--LAMMPS--ipr2',
        '2013--Henriksson-K-O-E--Fe-C--LAMMPS--ipr1',
        #'2008--Hepburn-D-J--Fe-C--LAMMPS--ipr1',
        #'2009--Kim-H-K--Fe-Ti-C--LAMMPS--ipr2'
    ]
    #pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Initialize pool of workers
    if num_runners > 1:
        pool = Pool(num_runners)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Prepare relax_dynamic at temp
    kwargs = deepcopy(global_kwargs)
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key]  
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    prepare.relax_dynamic.at_temp(database_name, run_directory_name, **kwargs)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

    # Run relax_dynamic
    multi_runners(database_name, run_directory_name, num_runners, pool=pool)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Close pool
    if pool is not None:
        pool.close()    