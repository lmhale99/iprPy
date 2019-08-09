from multiprocessing import Pool

from iprPy.workflow import multi_runners
import iprPy.workflow.prepare as prepare

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'testDB'
    run_directory_name = 'testDB_1'
    np = 3

    # Lammps and mpi commands
    lammps_command = 'lmp_mpi'
    #mpi_command = f'mpirun -np 8' # cluster
    
    # Potential-based modifiers
    pot_kwargs = {}
    pot_kwargs['id'] = '2002--Mishin-Y--Ni-Al--LAMMPS--ipr1'
    pot_kwargs['currentIPR'] = 'False'
    #pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

    # Prototype-based modifiers
    families = [
        'A1--Cu--fcc',
       # 'A2--W--bcc',
       # 'A3--Mg--hcp', 
       # 'A4--C--dc'
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