# coding: utf-8
# Standard Python libraries
from pathlib import Path
from copy import deepcopy
import shutil

import atomman as am

import numpy as np

import pandas as pd

# iprPy imports
from ..tools import aslist, filltemplate
from .. import load_calculation, load_run_directory, fix_lammps_versions
from ..input import parse

def master_prepare(database, input_script=None, debug=False, **kwargs):
    """
    Prepares one or more calculations according to the workflows used by the
    NIST Interatomic Potentials Repository.
    
    Parameters
    ----------
    database : iprPy.database.Database
        The database that will host the records for the prepared calculations.
    input_script : str or file-like object, optional
        The file, path to file, or contents of an input script containing
        parameters for preparing the calculation.
    debug : bool
        If set to True, will throw errors associated with failed/invalid
        calculation builds.  Default is False.
    **kwargs : str or list
        Allows for input parameters for preparing the calculation to be
        directly specified.  Any kwargs parameters that have names matching
        input_script parameters will overwrite the input_script values.
        Values must be strings or list of strings if allowed by the
        calculation for the particular parameter.
    """
    # Parse input_script
    if input_script is not None:
        temp = kwargs
        kwargs = parse(input_script)
        for key in temp:
            kwargs[key] = temp[key]

    # Get pools
    styles = aslist(kwargs.pop('styles'))
    np_per_runner = aslist(kwargs.pop('np_per_runner'))
    run_directory = aslist(kwargs.pop('run_directory'))
    if (len(styles) != len(np_per_runner) 
        or len(styles) != len(run_directory)):
        raise ValueError('number of styles, np_per_runner and run_directory terms do not match')

    for i in range(len(styles)):
        prepare_pool(database, styles[i], int(np_per_runner[i]),
                     run_directory[i], debug=debug, **kwargs)

def prepare_pool(database, styles, np_per_runner, run_directory, debug=False,
                 **kwargs):
    """
    Prepares a single pool of calculation styles according to the given kwargs.

    Parameters
    ----------
    database : iprPy.database.Database
        The database to prepare the calculations with.
    styles : str
        A space-delimited list of calculation styles to prepare.
    np_per_runner : int
        The number of processors that each runner will use.
    run_directory : str
        The path or name for the run_directory where the calculations will
        be prepared.
    debug : bool
        If set to True, will throw errors associated with failed/invalid
        calculation builds.  Default is False.
    **kwargs : str or list
        Allows for input parameters for preparing the calculation to be
        directly specified.  Any kwargs parameters that have names matching
        input_script parameters will overwrite the input_script values.
        Values must be strings or list of strings if allowed by the
        calculation for the particular parameter.
    """
    
    # Modify mpi_command using np_per_runner
    if 'mpi_command' in kwargs:
        if np_per_runner > 1:
            kwargs['mpi_command'] = kwargs['mpi_command'].format(np_per_runner=np_per_runner)
        else:
            del kwargs['mpi_command']

    # Loop over styles
    for style in styles.strip().split():

        # Separate style and branch
        if ':' in style:
            style, branch = style.split(':')
        else:
            branch = 'main'
        print(f'Preparing calculation {style} branch {branch}')

        # Load calculation
        calculation = load_calculation(style)

        # Build prepare input parameters
        params = calculation.master_prepare_inputs(branch=branch, **kwargs)

        # Prepare the calculation
        database.prepare(run_directory, calculation, debug=debug, **params)
        print()

    # Update lammps_commands as needed
    fix_lammps_versions(run_directory, **kwargs)