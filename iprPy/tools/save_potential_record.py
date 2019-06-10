# Standard Python libraries
from pathlib import Path
import shutil

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from . import iaslist
from .. import libdir

def save_potential_record(content, files=None, lib_directory=None,
                          record_style='potential_users_LAMMPS',
                          replace=False):
    """
    Saves a new potential_*LAMMPS record to the library directory.  The
    record's title is automatically taken as the record's id.

    Parameters
    ----------
    content : str or DataModelDict.DataModelDict
        The record content to save to the library directory.  Can be xml/json
        content, path to an xml/json file, or a DataModelDict.
    files : str or list, optional
        The directory path(s) to the parameter file(s) that the potential uses.
    lib_directory : str, optional
        The directory path for the library.  If not given, then it will use
        the iprPy/library directory.
    record_style : str, optional
        The record_style to save the record as.  Default value is
        'potential_users_LAMMPS', which should be used for user-defined
        potentials.
    replace : bool, optional
        If False (Default), will raise an error if a record with the same title
        already exists in the library.  If True, any matching records will be
        overwritten.

    Raises
    ------
    ValueError
        If replace=False and a record with the same title (i.e. id) already
        exists in the library.
    """
    # Load as DataModelDict and extract id as title
    content = DM(content)
    title = content['potential-LAMMPS']['id']

    # Set default lib_directory
    if lib_directory is None:
        lib_directory = libdir

    # Define record paths
    stylepath = Path(lib_directory, record_style)
    if not stylepath.is_dir():
        stylepath.mkdir()
    fname = Path(stylepath, title + '.json')
    potdir = Path(stylepath, title)
    
    # Save record
    if replace is False and fname.is_file():
        raise ValueError(f'Record {title} already exists')
    with open(fname, 'w') as recordfile:
        content.json(fp=recordfile, indent=4)

    # Copy parameter files
    if files is not None:
        if not potdir.is_dir():
            potdir.mkdir
        for fname in iaslist(files):
            shutil.copy(fname, potdir)