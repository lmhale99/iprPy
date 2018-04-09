# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# iprPy imports
from ..tools import aslist

def icalculations(database, record_style=None, symbol=None, family=None,
                  potential=None):
    """
    Iterates over calculation records in a database that match limiting
    conditions.
    
    Parameters
    ----------
    database : iprPy.Database 
        The database being accessed.
    record_style : str
        The record style to access.
    symbol : str or list of str, optional
        Single string element tag or list of element tags to limit by.  Only
        calcualtions that use element models for at least one of the listed
        symbols will be included.  If not given, then no limiting by symbol.
    family : str or list of str, optional
        Single family name or list of family names to limit by.  Only 
        calculations associated with the given system families will be 
        included.  If not given, then no limiting by family.
    potential : str or list of str, optional
        Single potential id or list of potential ids to limit by.  Only 
        calculations associated with the given potential will be included.
        If not given, then no limiting by potential.

    Yields
    ------
    iprPy.Record
        Each record from the database matching the limiting conditions.
    """
    
    df = []
    records = {}
    for record in database.iget_records(style=record_style):
        df.append(record.todict(full=False))
        records[record.name] = record
    df = pd.DataFrame(df)
    
    if family is not None:
        df = df[df.family.isin(aslist(family))]
    
    if potential is not None:
        df = df[df.potential_id.isin(aslist(potential))]
        
    if symbol is not None:
        check = np.empty(len(df), dtype=bool)
        for i, e in enumerate(df.symbols):
            check[i] = np.any(np.in1d(e, aslist(symbol)))
        df = df[check]
    
    for calc_key in df.calc_key.tolist():
        yield records[calc_key]