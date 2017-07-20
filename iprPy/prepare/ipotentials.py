from ..tools import aslist

import pandas as pd
import numpy as np

def ipotentials(database, record_style='potential-LAMMPS', 
                element=None, name=None, pair_style=None, 
                currentIPR=True):
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
    currentIPR -- boolean indicating if only the current IPR implementations of
                  the potentials are to be considered. If True, only the IPR# 
                  implementations with the highest # are included. If False, all
                  matching implementations will be used. Default value is True.
    
    Yields iprPy.Record objects for the associated potentials.    
    """
    
    df = []
    for record in database.iget_records(style=record_style):
        df.append(record.todict())
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