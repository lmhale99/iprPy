#!/usr/bin/env python
# coding: utf-8
import subprocess
from pathlib import Path
import pandas as pd
import numpy as np
import iprPy

def main():
    """
    Provides a quick survey of the status of all prepared records in the run
    directories and the slurm-submitted runners operating in them.

    NOTE: This was designed specifically for a system using the slurm queuing
    system and so may not work for all users and systems
    """
    
    # Build data
    jobs = squeue(user='lmh1', name='iprPy_1') # personal user id - change to your own
    logs = parse_runner_logs()
    rundirs, runners = check_run_directories()

    # Merge data
    logjobs = jobs.merge(logs, how='outer', on='jobid')
    runlogjobs = logjobs.merge(runners, how='outer', on='pid')

    # Loop over all run directories
    keys = ['jobid', 'pid', 'status', 'time', 'calcid', 'tmpdir',]# 'message']
    for i in rundirs.index:
        rundir = rundirs.loc[i]

        # List number of prepared calculations and number of runners
        print(rundir.run_directory, rundir.numcalcs, rundir.numrunners)
        dirjobs = runlogjobs[runlogjobs.run_directory == rundir.run_directory]
        
        # Print data for runners
        if len(dirjobs) > 0:
            print(dirjobs[keys])
        print()

    # List jobs with no associated bid files (usually finished)
    print('Unknown/finished jobs')
    nodir = runlogjobs[pd.isna(runlogjobs.run_directory)][keys]
    print(nodir)

    # Delete run logs for successfully finished jobs
    for jobid in nodir[nodir.status=='finished'].jobid.values:
        Path(f'runner_{jobid}.txt').unlink()

def squeue(**kwargs):
    """
    Calls squeue and collects the output.

    Parameters
    ----------
    kwargs : str, optional
        Any keyword arguments will be used to limit the search by
        only listing rows with the matching value for the key column name.
    
    Returns
    -------
    pandas.DataFrame
        The data returned by the squeue command.
    """

    # Call squeue and capture output lines
    r = subprocess.run('squeue', capture_output=True, encoding='UTF-8')
    lines = r.stdout.split('\n')

    # Column keys are given in the first line
    keys = [i.lower() for i in lines[0].split()]

    # Data is in remaining lines
    jobs = []
    for line in lines[1:]:
        terms = line.split()
        if len(terms) < len(keys):
            continue

        job = {}
        for i, key in enumerate(keys):
            job[key] = terms[i]
        jobs.append(job)

    jobs = pd.DataFrame(jobs)

    for key in kwargs:
        if key in keys and kwargs[key] != None:
            jobs = jobs[jobs[key] == kwargs[key]]

    return jobs.reset_index(drop=True)

def parse_runner_logs(root='.', glob='runner_*.txt'):
    """
    Parses all runner logs in a given directory.

    Parameters
    ----------
    root : str or path, optional
        The directory where the runner job logs are located. Default is the
        current working directory.
    glob : str, optional
        The glob wildcard-containing filename to use for identifying the
        runner job logs.  Default value is 'runner_*.txt'.
    
    Returns
    -------
    pandas.DataFrame
        The information parsed from the runner job logs.
    """
    alldata = []
    for filename in Path(root).glob(glob):
        alldata.append(parse_runner_log(filename))
    alldata = pd.DataFrame(alldata)

    return alldata

def parse_runner_log(filename):
    """
    Parses a runner job log file for the associated job id, process id, 
    temporary directory, runner status, and error message.

    Parameters
    ----------
    filename : str or path
        The runner log file to parse.

    Returns
    -------
    dict
        The parsed information.
    """
    # Set default values
    data = {}
    data['jobid'] = filename.stem.split('_')[1]
    data['pid'] = np.nan
    data['tmpdir'] = np.nan
    data['status'] = 'active'
    data['message'] = np.nan

    # Read lines from file
    with open(filename) as f:
        lines = f.readlines()

    # Loop over all lines
    for i, line in enumerate(lines):
        terms = line.split()
        if len(terms) == 0:
            continue

        # Extract pid from statement for runall runner
        if terms[0] == 'Runner' and len(terms) == 5:
            data['pid'] = terms[4]

        # Extract pid from statement for single calc runner
        elif terms[0] == 'Runner' and len(terms) == 7:
            data['pid'] = terms[6]

        # Extract tmpdir from associated statement
        elif terms[0] == 'using':
            data['tmpdir'] = terms[3]

        # Change status for successfully finished runners
        elif line.strip() == "Didn't find an open simulation":
            data['status'] = 'finished'
        elif line.strip() == "No simulations left to run":
            data['status'] = 'finished'
        elif line.strip() == "success":
            data['status'] = 'finished'

        # Anything else is an error message from the runner crashing
        else:
            data['status'] = 'crashed'
            data['message'] = ''.join(lines[i:])
            break

    return data


def check_run_directories():
    """
    Counts the number of calculations and bid files in all run directories and
    collects information for the bid files.

    Returns
    -------
    dirdata : pandas.DataFrame
        A list of the run directories and the number of calculation folders and
        bid files within each.
    biddata : pandas.DataFrame
        The processor id, calculation id, and run directory associated with
        each bid file in all run directories.
    """
    dirdata = []
    biddata = []
    
    # Loop over all run directories saved to iprPy's settings
    for run_directory_name in iprPy.Settings().list_run_directories:
        run_directory = iprPy.load_run_directory(run_directory_name)

        if run_directory.is_dir():
            # Build dirdata info
            ddata = {}
            ddata['run_directory'] = run_directory_name
            ddata['numcalcs'] = len([i for i in run_directory.glob('*')])
            ddata['numrunners'] = len([i for i in run_directory.glob('*/*.bid')])

            for bidfile in run_directory.glob('*/*.bid'):
                # Build biddata info
                bdata = {}
                bdata['pid'] = bidfile.stem
                bdata['calcid'] = bidfile.parent.name
                bdata['run_directory'] = run_directory_name
                biddata.append(bdata)
            dirdata.append(ddata)

    return pd.DataFrame(dirdata), pd.DataFrame(biddata)

if __name__ == '__main__':
    main()
