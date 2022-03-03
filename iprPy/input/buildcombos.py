# coding: utf-8

# Standard Python libraries
from typing import Optional, Tuple

# iprPy imports
from .buildcombos_functions import loaded

__all__ = ['buildcombos']

def buildcombos(style: str,
                database,
                keys: list,
                content_dict: Optional[dict] = None,
                **kwargs) -> Tuple[dict, dict]:
    """
    Wrapper function for the modular buildcombos styles

    Parameters
    ----------
    style : str
        The buildcombos style to use
    database : iprPy.database.Database
        The database to use in building combos
    keys : list
        The calculation multikey set to build combos for
    content_dict : dict, optional
        Contains loaded file content.  If not given, an empty
        dict will be created
    kwargs : any
        Additional keyword arguments will be used to limit which records from
        the database are used in building combos values.
    
    Returns
    -------
    inputs : dict
        Contains the values generated for each key
    content_dict : dict
        Contains loaded file content
    """
    return loaded[style](database, keys, content_dict=content_dict, **kwargs)
