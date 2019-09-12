from copy import deepcopy
from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_1'
    np = 0

    # Generic settings
    global_kwargs = {}
    global_kwargs['lammps_command'] = 'lmp_mpi'
    global_kwargs['parent_method'] = 'dynamic'

    # Potential-based modifiers
    pot_kwargs = {}
    #pot_kwargs['id'] = [
    #    '2014--Liyanage-L-S-I--Fe-C--LAMMPS--ipr2',
    #    '2013--Henriksson-K-O-E--Fe-C--LAMMPS--ipr1',
    #    '2008--Hepburn-D-J--Fe-C--LAMMPS--ipr1',
    #    '2009--Kim-H-K--Fe-Ti-C--LAMMPS--ipr2'
    #]
    #pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare phonon
    kwargs = deepcopy(global_kwargs)
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    prepare.phonon.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run small sims
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()    