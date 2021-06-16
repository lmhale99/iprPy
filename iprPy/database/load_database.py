from .. import settings
import datamodelbase

def load_database(name=None, style=None, host=None, **kwargs):
    """
    Loads a database object.  Can be either loaded from stored settings or
    by defining all needed access information.
    
    Parameters
    ----------
    name : str, optional
        The name assigned to a pre-defined database.  If given, can be the only
        parameter.
    style : str, optional
        The database style to use.
    host : str, optional
        The URL/file path where the database is hosted.
    kwargs : dict, optional
        Any other keyword parameters defining necessary access information.
        Allowed keywords are database style-specific.
    
    Returns
    -------
    Subclass of datamodelbase.Database
        The database object.
    """
    return datamodelbase.load_database(name=name, style=style, host=host,
                                       settings=settings, **kwargs)
