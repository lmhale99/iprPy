#!/usr/bin/env python
# coding: utf-8

# Standard Python libraries
from typing import Union
import argparse
import time

import iprPy

def sleep_until_done(run_directory_name: str,
                     init_sleep_time: Union[int, str] = '6h',
                     delta_sleep_time: Union[int, str] = '30m',
                     verbose: bool = False):
    """
    Utility function for emperor/commander workflow jobs to sleep while spawned
    runner jobs work through existing calculations in a given run_directory.

    Parameters
    ----------
    run_directory_name : str
        The run_directory name to check for unfinished calculations.
    init_sleep_time : int or str, optional
        The time to sleep before performing the first calculation count.  Can
        be given in seconds (int value or str containing 's' or just the number),
        minutes (str containing 'm'), or hours (str containing 'h').  Default
        value is '6h'.
    delta_sleep_time : int or str, optional
        The time to sleep between calculation counts.  Can be given in seconds
        (int value or str containing 's' or just the number), minutes (str
        containing 'm'), or hours (str containing 'h').  Default value is '6h'.
    verbose : bool, optional
        If set to True, the number of remaining calculations will be printed for
        each check.
    """

    # Load run_directory
    run_directory = iprPy.load_run_directory(run_directory_name)

    # Interpret time values
    init_sleep_time = interpret_str_time(init_sleep_time)
    delta_sleep_time = interpret_str_time(delta_sleep_time)

    # First sleep
    time.sleep(init_sleep_time)

    # Count remaining calculations
    count = len([d for d in run_directory.iterdir()])
    if verbose:
        print(count, 'calculations remaining to run', flush=True)

    while count > 0:
        # Sleep between counts
        time.sleep(delta_sleep_time)

        # Count remaining calculations
        count = len([d for d in run_directory.iterdir()])
        if verbose:
            print(count, 'calculations remaining to run', flush=True)


def interpret_str_time(time: Union[str, int]) -> int:
    
    if isinstance(time, str):
        if 's' in time:
            time = int(time.split('s')[0].strip())
        elif 'm' in time:
            time = int(time.split('m')[0].strip())
            time *= 60
        elif 'h' in time:
            time = int(time.split('h')[0].strip())
            time *= 3600
        else:
            time = int(time)

    return time
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='sleep until all prepared iprPy calcs in a run_directory finish')
    
    parser.add_argument('run_directory_name',
                        help='run_directory name')
    parser.add_argument('-i', '--initsleeptime', default='6h',
                        help='how long to sleep before first calc count')
    parser.add_argument('-s', '--deltasleeptime', default='30m',
                        help='how long to sleep between calc counts')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print # of calcs remaining for each check')

    args = parser.parse_args()

    sleep_until_done(args.run_directory_name,
                     init_sleep_time = args.initsleeptime,
                     delta_sleep_time = args.deltasleeptime,
                     verbose = args.verbose)
