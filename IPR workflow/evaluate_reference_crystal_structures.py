from pathlib import Path
from multiprocessing import Pool

import iprPy

if __name__ == '__main__':
    
    # Database, run directory and number of processors to use
    database_name = 'demo'
    run_directory_name = 'master_2'
    np = 0

    # Paths to compiled results
    csv_path = Path(iprPy.rootdir, '..', 'IPR workflow', 'csv')
    crystal_match_file = Path(csv_path, 'reference_prototype_match.csv')



# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Initialize pool of workers
    if np > 1:
        pool = Pool(np)
    else:
        pool = None
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Prepare crystal_space_group for prototypes and references
    iprPy.workflow.prepare.crystal_space_group.protoref(database_name, run_directory_name)

    # Run 
    iprPy.workflow.multi_runners(database_name, run_directory_name, np, pool=pool)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # Process references and identify prototype matches
    iprPy.workflow.process.references(database_name, crystal_match_file)