from .. import record_todict
from ..tools import aslist

import pandas as pd
import numpy as np


def ipotentials(database, element=None, name=None, pair_style=None, record_type='LAMMPS-potential'):
    """
    Iterates over potentials in a database that match limiting conditions.
    
    Arguments:
    database -- an iprPy.Database object for the database being accessed
    
    Keyword Arguments:
    element -- single string element tag or list of element tags. Only 
               potentials that contain models for at least one of the listed
               elements will be returned. Default value is None (i.e. no 
               selection by element).
    name -- single string name or list of names for the potentials to include.
            Default value is None (i.e. no selection by name).
    pair_style -- single string LAMMPS pair_style type or list of pair_style 
                  types that the potentials must be to be returned. Default
                  value is None (i.e. no selection by pair_style).
    record_type -- string name for the record type (i.e. template) to use.
                   Default value is 'LAMMPS-potential'.
    
    Returns the potential's name, the potential's record as a string and the 
    potential's archives as an open Tarfile object.    
    """
    
    df = []
    for record in database.iget_records(record_type):
        df.append(record_todict(record, record_type=record_type))
    df = pd.DataFrame(df)
    
    if name is not None:
        df = df[df.pot_id.isin(aslist(name))]
    
    if pair_style is not None:
        df = df[df.pair_style.isin(aslist(pair_style))]
        
    if element is not None:
        check = np.empty(len(df), dtype=bool)
        for i, e in enumerate(df.elements):
            check[i] = np.any(np.in1d(e, aslist(element)))
        df = df[check]
        
    for pot_id in df.pot_id.tolist():
        record = database.get_records(key=pot_id)[0]
        archive = database.get_archive(key=pot_id)
        
        yield pot_id, record, archive