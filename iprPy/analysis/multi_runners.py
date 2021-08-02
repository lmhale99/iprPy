from .. import load_database, load_run_directory

def single_runner(database_name, run_directory_name):
    """Utility function for starting multiple runners using multiprocessing"""
    database = load_database(database_name)
    run_directory = load_run_directory(run_directory_name)
    database.runner(run_directory)

def multi_runners(database_name, run_directory_name, processes, pool=None):
    """
    Starts multiple runners as subprocesses

    Parameters
    ----------
    database_name : str
        The name of the iprPy database where the records are stored
    run_directory_name : str
        The name of the iprPy run_directory to prepare calculations in
    processes : int
        The number of workers from the pool to call. If < 1, then no runners
        will be started (i.e. this function will do nothing)
    pool : multiprocessing.Pool, optional
        The pool of subprocess workers to use. Not needed for processes < 2
    """

    if processes > 0:    
        print(f'Starting {processes} runners in {run_directory_name} for {database_name}', flush=True)

        if processes == 1:
            single_runner(database_name, run_directory_name)
        else:
            results = []
            
            # Start runners on the workers
            for i in range(processes):
                results.append(pool.apply_async(single_runner, args=(database_name, run_directory_name,)))
            
            # Wait for all workers to finish
            for i in range(processes):
                results[i].get()

        print()