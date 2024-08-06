#!/usr/bin/env python
# coding: utf-8

# Standard Python libraries

from pathlib import Path
import shlex
import subprocess
import argparse

import iprPy

def multi_runner_slurm(database_name,
                       run_directory_name,
                       ncores = 1,
                       temp = True,
                       njobs = None,
                       minjobs = 1,
                       maxjobs = 50,
                       percentjobs = 10,
                       individualjobs = False,
                       dryrun = False
                       ):


    # Set slurm script based on ncores
    if ncores == 1:
        cmd = 'sbatch iprPy_slurm'
    else:
        cmd = f'sbatch iprPy_slurm_{ncores}'
    
    # Add database and run directory fields
    cmd += f' runner {database_name} {run_directory_name}'

    # Add temp option
    if temp is True:
        cmd += ' -t'

    run_directory = iprPy.load_run_directory(run_directory_name)
    
    if individualjobs is False:
        # Count number of calcs and figure out how many jobs to submit
        count = len([calc for calc in run_directory.glob('*')])
        bidcount = len([bid for bid in run_directory.glob('*/*.bid')])

        if count == 0:
            print('No calcs to run')
            return
            
        if njobs is None:
            njobs = round(count * percentjobs / 100)
            if njobs < minjobs:
                njobs = minjobs
            elif njobs > maxjobs:
                njobs = maxjobs
            
        for i in range(njobs - bidcount):
            if dryrun:
                print(cmd)
            else:
                subprocess.run(shlex.split(cmd))
    
    elif individualjobs is True:
        # Submit a separate job for each calc
        for i, calc in enumerate(run_directory.glob('*')):
            calc_name = calc.name
            cmd_calc = f'{cmd} -c {calc_name}'
            if dryrun:
                print(cmd_calc)
            else:
                subprocess.run(shlex.split(cmd_calc))
            
            if njobs is not None and i == njobs:
                break
    
    else:
        raise TypeError('individualjobs must be a bool')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='iprPy multi runner slurm submitter')
    
    parser.add_argument('database',
                        help='database name')
    parser.add_argument('run_directory',
                        help='run_directory name')
    parser.add_argument('-c', '--ncores', default=1, type=int,
                        help='number of cores per job')
    parser.add_argument('-t', '--temp', action='store_true',
                        help='indicates that the calculations are to run in a temporary directory')
    parser.add_argument('-i', '--individualjobs', action='store_true',
                        help='indicates that all calculations are to run as separate jobs')
    parser.add_argument('-n', '--njobs', default=None, type=int,
                        help='number of jobs to submit')
    parser.add_argument('--minjobs', default=1, type=int,
                        help='number of jobs to submit')
    parser.add_argument('--maxjobs', default=50, type=int,
                        help='number of jobs to submit')
    parser.add_argument('--percentjobs', default=10, type=int,
                        help='number of jobs to submit')

    args = parser.parse_args()

    multi_runner_slurm(args.database,
                       args.run_directory,
                       ncores = args.ncores,
                       temp = args.temp,
                       njobs = args.njobs,
                       minjobs = args.minjobs,
                       maxjobs = args.maxjobs,
                       percentjobs = args.percentjobs,
                       individualjobs = args.individualjobs,
                       #dryrun = True,
                       )
