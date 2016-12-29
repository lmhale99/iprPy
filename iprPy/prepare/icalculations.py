from ..tools import aslist

import pandas as pd
import numpy as np

def icalculations(database, symbol=None, prototype=None, potential=None, record_style=None):
    """
    Iterates over calculation records in a database that match limiting conditions.
    
    Arguments:
    database -- an iprPy.Database object for the database being accessed
    
    Keyword Arguments:
    symbol -- single string element tag or list of element symbols. Only 
              potentials that contain models for at least one of the listed
              symbols will be returned. Default value is None (i.e. no 
              selection by element).
    prototype -- single string name or list of names for the prototypes to 
                 include. Default value is None (i.e. no selection by 
                 prototype).
    potential -- single string name or list of names for the prototypes to 
                 include.
    record_style -- string name for the record style (i.e. template) to use.
    
    Yields iprPy.Record objects for the associated calculations.    
    """
    
    df = []
    for record in database.iget_records(style=record_style):
        df.append(record.todict(full=False))
    df = pd.DataFrame(df)
    
    if prototype is not None:
        df = df[df.prototype.isin(aslist(prototype))]
    
    if potential is not None:
        df = df[df.potential_id.isin(aslist(potential))]
        
    if symbol is not None:
        check = np.empty(len(df), dtype=bool)
        for i, e in enumerate(df.symbols):
            check[i] = np.any(np.in1d(e, aslist(symbol)))
        df = df[check]
        
    for calc_key in df.calc_key.tolist():
        yield database.get_record(name=calc_key, style=record_style)