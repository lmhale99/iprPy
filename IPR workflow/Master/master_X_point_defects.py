from multiprocessing import Pool

from multi_runners import multi_runners
import workflow_prepare as prepare

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_4'
    np = 0

    # Lammps and mpi commands
    lammps_command = 'lmp_mpi'
    #mpi_command = f'mpirun -np 8' # cluster
    
    # Potential-based modifiers
    pot_kwargs = {}
    #pot_kwargs['id'] = '1999--Mishin-Y--Al--LAMMPS--ipr1'
    pot_kwargs['currentIPR'] = 'False'
    pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Prototype-based modifiers
    families = [
       # 'A1--Cu--fcc',
       # 'A2--W--bcc',
        'A3--Mg--hcp', 
        'A4--C--dc'
        ]

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
    
    # Prepare each family separately (avoids invalid calculations being checked)
    for family in families:
        kwargs['parent_family'] = family
        kwargs['defect_family'] = family

        prepare.point_defect_static.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run small sims
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()    