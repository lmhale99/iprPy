import iprPy


def runner_parallel_job(database_name,
                        run_directory_name,
                        calc_name,
                        temp):
    database = iprPy.load_database(database_name)
    database.runner(run_directory_name, calc_name=calc_name, temp=temp)


def runrun_parallel(database_name,
                    run_directory_name,
                    mp_pool,
                    calc_names=None,
                    temp = True):
    if calc_names is None:
        database = iprPy.load_database(database_name)
        runner = database.runmanager(run_directory_name)
        calc_names = runner.calclist
    params = [(database_name, run_directory_name, calc_name, temp) for calc_name in calc_names]
    results = [mp_pool.apply_async(runner_parallel_job, p) for p in params]