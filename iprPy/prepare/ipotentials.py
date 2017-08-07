from __future__ import division, absolute_import, print_function

from ..tools import aslist

import pandas as pd
import numpy as np

def ipotentials(database, record_style='potential_LAMMPS', 
                element=None, name=None, pair_style=None, 
                currentIPR=True):
    """
    Iterates over potential records in a database that match limiting 
    conditions.
    
    Parameters
    ----------
    database : iprPy.Database 
        The database being accessed.
    record_style : str, optional
        The record style to access (Default is 'potential_LAMMPS').
    element : str or list of str, optional
        Single string element tag or list of element tags to limit by.  Only
        potentials that have element models for at least one of the listed
        elements will be included.  If not given, then no limiting by element.
    name : str or list of str, optional
        Single potential id or list of potential ids to limit by.  Only 
        potentials with the given potential id will be included.  If not
        given, then no limiting by name.
    pair_style : str or list of str, optional
        Single LAMMPS pair_style or list of LAMMPS pair_styles to limit by.
        Only potentials with the given pair_style will be included.  If not
        given, then no limiting by pair_style.
    currentIPR : bool
        If True, only the current IPR implementations of the potentials will
        be included, i.e. the record names end with --IPR#, and # is the
        highest for all records associated with the same potential id. If 
        False, all matching implementations will be included. (Default is 
        True.)
    
    Yields
    ------
    iprPy.Record 
        Each record from the database matching the limiting conditions.
    """
    
    df = []
    records = {}
    for record in database.iget_records(style=record_style):
        df.append(record.todict())
        records[record.name] = record
    df = pd.DataFrame(df)
    
    # Limit by potential name
    if name is not None:
        df = df[df.pot_id.isin(aslist(name))]
    
    # Limit by pair_style
    if pair_style is not None:
        df = df[df.pair_style.isin(aslist(pair_style))]
    
    # Limit by element
    if element is not None:
        check = np.empty(len(df), dtype=bool)
        for i, e in enumerate(df.elements):
            check[i] = np.any(np.in1d(e, aslist(element)))
        df = df[check]
    
    # Limit to only current IPR implementations
    if currentIPR is True:
        
        # Extract versionstyle and versionnumber
        versionstyle = []
        versionnumber = []
        for name in df['id'].values:
            version = name.split('--')[-1]
            try:
                versionnumber.append(int(version[-1]))
            except:
                versionnumber.append(np.nan)
                versionstyle.append(version)
            else:
                versionstyle.append(version[:-1])

        df['versionstyle'] = versionstyle
        df['versionnumber'] = versionnumber
        
        # Loop through unique potential id's
        includeid = []
        for pot_id in np.unique(df.pot_id.values):
            check_df = df[df.pot_id == pot_id]
            check_df = check_df[check_df.versionstyle == 'ipr']
            check_df = check_df[check_df.versionnumber == check_df.versionnumber.max()]
            if len(check_df) == 1:
                includeid.append(check_df['id'].values[0])
            elif len(check_df) > 1:
                raise ValueError('Bad currentIPR check for '+pot_id)
        
        # Limit df by includeid potentials
        df = df[df['id'].isin(includeid)]
                
    for name in df['id'].values:
        yield database.get_record(name=name, style=record_style)