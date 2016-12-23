from .. import record_todict
from ..tools import aslist

import pandas as pd

def iprototypes(database, natypes=None, name=None, spacegroup=None, crystalfamily=None, pearson=None, record_type='crystal-prototype'):
    """
    Iterates over potentials in a database that match limiting conditions.
    
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
    record_type -- string name for the record type (i.e. template) to use.
                   Default value is 'crystal-prototype'.
    
    Returns the prototype's id and the prototype's record as a string.    
    """
    
    df = []
    for record in database.iget_records(record_type):
        df.append(record_todict(record, record_type=record_type))
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
        record = database.get_records(key=proto_id)[0]
        
        yield proto_id, record