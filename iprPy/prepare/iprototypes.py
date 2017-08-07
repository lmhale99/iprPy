from __future__ import division, absolute_import, print_function

from ..tools import aslist

import pandas as pd

def iprototypes(database, record_style='crystal_prototype', natypes=None,
                name=None, spacegroup=None, crystalfamily=None, pearson=None):
    """
    Iterates over crystal prototype records in a database that match limiting 
    conditions.
    
    Parameters
    ----------
    database : iprPy.Database 
        The database being accessed.
    record_style : str, optional
        The record style to access (Default is 'crystal_prototype').
    name : str or list of str, optional
        Single prototype name or list of prototype names to limit by.  Only 
        prototypes with id, name, prototype, or Strukturbericht values matching
        name will be included.  If not given, then no limiting by name.
    spacegroup : str or list of str, optional
        Single spacegroup or list of spacegroups to limit by.  Only 
        prototypes with space-group number, Hermann-Maguin, or Schoenflies
        values matching spacegroup will be included.  If not given, then no
        limiting by spacegroup.
    crystalfamily : str or list of str, optional
        Single crystal family name or list of crystal family names to limit
        by.  Only prototypes with the matching crystalfamily will be included.
        If not given, then no limiting by crystalfamily.
    pearson : str or list of str, optional
        Single Pearson symbol or list of Pearson symbols to limit by.  Only 
        prototypes with Pearson-symbol terms matching pearson will be 
        included.  If not given, then no limiting by pearson.

    Yields
    ------
    iprPy.Record 
        Each record from the database matching the limiting conditions.
    """
    
    df = []
    for record in database.iget_records(style=record_style):
        df.append(record.todict())
    df = pd.DataFrame(df)
    
    if natypes is not None:
        df = df[df.natypes.isin(aslist(natypes))]
        
    if crystalfamily is not None:
        df = df[df.crystal_family.isin(aslist(crystalfamily))]
        
    if pearson is not None:
        df = df[df.Pearson_symbol.isin(aslist(pearson))]
        
    if name is not None:
        df = df[(df.id.isin(aslist(name))) |
                (df.name.isin(aslist(name))) |
                (df.prototype.isin(aslist(name))) |
                (df.Strukturbericht.isin(aslist(name))) ]
        
    if spacegroup is not None:
        df = df[(df.sg_HG.isin(aslist(spacegroup))) |
                (df.sg_Schoen.isin(aslist(spacegroup))) |
                (df.sg_number.isin(aslist(spacegroup)))]
        
    for proto_id in df.id.tolist():
        yield database.get_record(name=proto_id, style=record_style)