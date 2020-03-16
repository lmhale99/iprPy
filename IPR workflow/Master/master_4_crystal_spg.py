from copy import deepcopy
from pathlib import Path

from multiprocessing import Pool

from iprPy.workflow import prepare, multi_runners, process

from iprPy.tools import aslist

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'master'
    run_directory_name = 'master_1'
    num_runners = 0
    np_per_runner = 1
    run_location = 'local'

    # Generic settings
    global_kwargs = {}    

    # Paths to compiled results
    crystal_match_file = Path('..', 'csv', 'reference_prototype_match.csv')
    all_crystals_file = Path('..', 'csv', f'{database_name}_all_crystals.csv')
    unique_crystals_file = Path('..', 'csv', f'{database_name}_unique_crystals.csv')

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Initialize pool of workers
    if num_runners > 1:
        pool = Pool(num_runners)
    else:
        pool = None
  
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Prepare crystal_space_group
    kwargs = deepcopy(global_kwargs)

    prepare.crystal_space_group.relax(database_name, run_directory_name, **kwargs)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Run crystal_space_group
    multi_runners(database_name, run_directory_name, num_runners, pool=pool)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Close pool
    if pool is not None:
        pool.close()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    
    # Call process relaxation results and generate relaxed_crystal records
    process.relaxed(database_name, crystal_match_file, all_crystals_file, unique_crystals_file)