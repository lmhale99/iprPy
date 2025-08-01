from pathlib import Path
import shlex
import subprocess
import time

import iprPy

def runrun(
           database_name,
           run_directory_name,
           calc_names = None,
           mp_pool = None):
    



def runrun_single(database_name,
                  run_directory_name,
                  calc_names = None,
                  temp = True,):
    """
    Runs the prepared jobs 
    Start single runner within the """
    database = iprPy.load_database(database_name)
    runner = database.runmanager(run_directory_name)

    if calc_names is None:
        calc_names = runner.calclist

    for calc_name in calc_names:
        runner.run(calc_name, temp=temp)





def runrun_slurm_individual_jobs(database_name,
                                 run_directory_name,
                                 calc_names = None,
                                 temp = True,
                                 ncores = 1,
                                 wait = False):
    
    # Find all free calcs in the run_directory
    database = iprPy.load_database(database_name)
    runner = database.runmanager(run_directory_name)
    all_calc_names = runner.calclist

    if calc_names is None:
        # Prepare for all calcs
        calc_names = all_calc_names
    else:
        # Prepare only free calcs from the given list
        calc_names = list(set(calc_names).union(all_calc_names))

    # Set slurm script based on ncores
    if ncores == 1:
        script = 'iprPy_slurm'
    else:
        script = f'iprPy_slurm_{ncores}'
    
    # Add temp option
    if temp is True:
        temp_flag = ' -t'
    else:
        temp_flag = ''

    # Build slurm command and submit the job
    for calc_name in calc_names:
        cmd = f'sbatch {script} {database_name} {run_directory_name}{temp_flag} -c {calc_name}'
        subprocess.run(shlex.split(cmd))
    
    # Wait until all finished if requested
    if wait:
        run_directory = iprPy.load_run_directory(run_directory_name)
        while True:
            finished = True
            for calc_name in calc_names:
                if Path(run_directory, calc_name).exists():
                    finished = False
                    break
            if finished:
                break
            else:
                time.sleep(300)

def runrun_slurm(database_name,
                 run_directory_name,
                 temp = True,
                 ncores = 1,
                 njobs = None,
                 minjobs = 1,
                 maxjobs = 50,
                 percentjobs = 10,
                 wait = False):

    # Set slurm script based on ncores
    if ncores == 1:
        script = 'iprPy_slurm'
    else:
        script = f'iprPy_slurm_{ncores}'
    
    # Add temp option
    if temp is True:
        temp_flag = ' -t'
    else:
        temp_flag = ''

    # Build the slurm job submission command
    cmd = f'sbatch {script} {database_name} {run_directory_name}{temp_flag}'

    # Count number of calcs and figure out how many jobs to submit
    run_directory = iprPy.load_run_directory(run_directory_name)
    count = len([calc for calc in run_directory.glob('*')])
    bidcount = len([bid for bid in run_directory.glob('*/*.bid')])

    # Decide on njobs based on percentjobs, minjobs and maxjobs
    if njobs is None:
        njobs = round(count * percentjobs / 100)
        if njobs < minjobs:
            njobs = minjobs
        elif njobs > maxjobs:
            njobs = maxjobs
    
    # Submit runner jobs so njobs total are active
    for i in range(njobs - bidcount):
        subprocess.run(shlex.split(cmd))
    
    # Wait until all finished if requested
    if wait:
        run_directory = iprPy.load_run_directory(run_directory_name)
        while True:
            count = len([calc for calc in run_directory.glob('*')])
            if count == 0:
                break
            else:
                time.sleep(300)