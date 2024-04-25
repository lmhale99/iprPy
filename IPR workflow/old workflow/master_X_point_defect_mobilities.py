from multiprocessing import Pool

import iprPy
from iprPy.workflow import multi_runners
import iprPy.workflow.prepare as prepare

if __name__ == '__main__':

    # Database, run directory and number of processors to use
    database_name = 'testDB'
    run_directory_name = 'testDB_1'
    database = iprPy.load_database(name=database_name)
    run_directory = iprPy.load_run_directory(name=run_directory_name)
    

    
    np = 1
    
    # Lammps and mpi commands
    lammps_command = 'lmp_mpi -p 8x1'
    mpi_command = 'mpiexec -localonly 8'
    number_replicas = 8
    
    
    # Potential-based modifiers
    pot_kwargs = {}
    #pot_kwargs['id'] = '2008--Zhou-X-W--Pd-H--LAMMPS--ipr1'
    pot_kwargs['currentIPR'] = 'False'
    pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']
    
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
    # Prepare point_defect_mobility
    kwargs = {}
    kwargs['lammps_command'] = lammps_command
    kwargs['mpi_command'] = mpi_command
    
    # Determining the number of impurities you are interested in for defect mobility calculations.
    # kwargs['defectmobility_allowable_impurity_numbers'] should be defined as a list for each set of impurities you are interested in
    # kwargs['defectmobility_allowable_impurity_numbers'] = [0, 1, 2]
    
    # Defining any limitations on the impurities used in defect calculations
    # impurity_list defines a list of impurities (as symbols) to use
    # impurity_blacklist defines a list of impurities (as symbols) to not use
    # Only one can be defined, otherwise an error will popup
    
    #kwargs['defectmobility_impurity_list'] = ['Cu', 'Nb']
    #kwargs['defectmobility_impurity_blacklist'] = ['Nb']
    
    
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
     
    # Used to define a list of possible composition for the matrix
    
    #kwargs[f'parent_composition'] = 'Ni'
    
    # Sets the number of steps we want to check.  This lets us calculate all of the easy ones, while the others can be come back to later
    
    kwargs['dumpsteps'] = '2000'
    kwargs['minsteps'] = '2000'
    kwargs['climbsteps'] = '2000'
    
    # Prepare each family separately (avoids invalid calculations being checked)
    for family in families:
        kwargs['parent_family'] = family
        kwargs['defectmobility_family'] = family
        prepare.point_defect_mobility.main(database_name, run_directory_name, **kwargs)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Run small sims
    database.runner(run_directory)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if pool is not None:
        pool.close()    