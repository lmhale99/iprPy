from ..tools import aslist

import pandas as pd

def iprototypes(database, record_style='crystal-prototype', natypes=None, name=None, spacegroup=None, crystalfamily=None, pearson=None):
    """
    Iterates over crystal prototype records in a database that match limiting 
    conditions.
    
    Arguments:
    database -- an iprPy.Database object for the database being accessed
    
    Keyword Arguments:
    natypes -- int or list of ints for the number of atom types (i.e. sites) 
               that the prototype must have. Default value is None (i.e. no 
               selection by natypes)
    name -- single string name or list of names for the prototypes to include.
            Search uses potential's id, name, prototype, and Strukturbericht 
            terms. Default value is None (i.e. no selection by name).
    spacegroup -- single term or list of terms for limiting by crystal space 
                   group, Search uses space group number, H-M and Schoenflies 
                   names. Default value is None (i.e. no selection by space 
                   group).
    crystalfamily -- single string or list of strings for the crystal families
                      to limit returned prototypes by. Default value is None 
                      (i.e. no selection by crystal family).
    pearson -- single string or list of strings for Pearson symbols to limit 
               search by. Default value is None (i.e. no selection by Pearson 
               symbol).
    record_style -- string name for the record style (i.e. template) to use.
                    Default value is 'crystal-prototype'.
    
    Yields iprPy.Record objects for the associated crystal prototypes.    
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