from pathlib import Path
from multiprocessing import Pool

import iprPy
from iprPy.workflow import prepare, multi_runners, process

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'test'
    run_directory_name = 'test_1'
    np = 4

    # Paths to compiled results
    crystal_match_file = Path('reference_prototype_match.csv')

    ref_kwargs = {}
    ref_kwargs['composition'] = ['Al', 'Ni']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare crystal_space_group for prototypes
    kwargs = {}
    prepare.crystal_space_group.prototype(database_name, run_directory_name, **kwargs)

    # Prepare crystal_space_group for references
    kwargs = {}
    for key in ref_kwargs:
        kwargs[f'ref_{key}'] = ref_kwargs[key]
    prepare.crystal_space_group.reference(database_name, run_directory_name, **kwargs)

    # Run 
    multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Process references and identify prototype matches
    process.references(database_name, crystal_match_file)