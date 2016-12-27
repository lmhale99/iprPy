from ..tools import aslist

import pandas as pd
import numpy as np

def ipotentials(database, element=None, name=None, pair_style=None, record_style='LAMMPS-potential'):
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
    record_style -- string name for the record type (i.e. template) to use.
                   Default value is 'LAMMPS-potential'.
    
    Yields iprPy.Record objects for the associated potentials.    
    """
    
    df = []
    for record in database.iget_records(style=record_style):
        df.append(record.todict())
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
        yield database.get_record(name=pot_id, style=record_style)