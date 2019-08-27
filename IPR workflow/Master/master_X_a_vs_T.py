from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_4'
    np = 0

    # Lammps and mpi commands
    lammps_command = 'lmp_mpi'
    mpi_command = f'mpirun -np 8' # cluster
    
    # Potential-based modifiers
    pot_kwargs = {}
    pot_kwargs['id'] = [
        '2014--Liyanage-L-S-I--Fe-C--LAMMPS--ipr2',
        '2013--Henriksson-K-O-E--Fe-C--LAMMPS--ipr1',
        '2008--Hepburn-D-J--Fe-C--LAMMPS--ipr1',
        '2009--Kim-H-K--Fe-Ti-C--LAMMPS--ipr2'
    ]
    #pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare point_defect_static
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

        prepare.relax_dynamic.at_temp(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run small sims
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()    