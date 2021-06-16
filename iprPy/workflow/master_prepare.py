# coding: utf-8

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
from .. import load_calculation, load_database, load_run_directory
from ..input import parse
from ..database import prepare
from . import fix_lammps_versions

def master_prepare(input_script=None, **kwargs):
    """
    Prepares one or more calculations according to the workflows used by the
    NIST Interatomic Potentials Repository.
    
    Parameters
    ----------
    input_script : str or file-like object, optional
        The file, path to file, or contents of an input script containing
        parameters for preparing the calculation.
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

    # Load database
    database_name = kwargs.pop('database')
    database = load_database(database_name)

    # Get pools
    styles = aslist(kwargs.pop('styles'))
    np_per_runner = aslist(kwargs.pop('np_per_runner'))
    run_directory = aslist(kwargs.pop('run_directory'))
    if (len(styles) != len(np_per_runner) 
        or len(styles) != len(run_directory)):
        raise ValueError('number of styles, np_per_runner and run_directory terms do not match')

    for i in range(len(styles)):
        prepare_pool(database, styles[i], int(np_per_runner[i]),
                     run_directory[i], **kwargs)

def prepare_pool(database, styles, np_per_runner, run_directory, **kwargs):
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
        prepare(database, run_directory, calculation, **params)
        print()

    # Update lammps_commands as needed
    fix_lammps_versions(run_directory, **kwargs)