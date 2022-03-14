# coding: utf-8

# Standard Python libraries
from typing import Any

def dict_insert(d: dict,
                key: Any,
                value: Any,
                **kwargs):
    """
    Adds a new key, value pair into a dictionary by inserting it
    relative to a known key.
    
    Parameters
    ----------
    d : dict
        The dict to add the new key, value to.
    key : any
        The new dict key to insert.
    value : any
        The dict value to assign to d[key].
    before : any, optional
        If given, then the new key will be inserted before this key.  Cannot be
        given with after.
    after : any, optional
        If given, then the new key will be inserted after this key.  Cannot be
        given with before
    """
    if len(kwargs) == 0:
        # Set normally if no kwargs given.
        d[key] = value
        return

    elif len(kwargs) == 1:
        if 'before' in kwargs:
            try:
                i = list(d.keys()).index(kwargs['before'])
            except:
                # Set normally if ref key not found
                d[key] = value
                return
        elif 'after' in kwargs:
            try:
                i = list(d.keys()).index(kwargs['after']) + 1
            except:
                # Set normally if ref key not found
                d[key] = value
                return
        else:
            raise TypeError(f"dict_insert() got an unexpected keyword argument '{list(kwargs.keys())[0]}'")
    else:
        raise ValueError('Only one kwarg (before or after) can be given')
    
    # Remove d if currently in d
    if key in d:
        del d[key]
        
    # Pop all keys after previous
    nd = {}
    for k in list(d.keys())[i:]:
        nd[k] = d.pop(k)

    # Set key, value
    d[key] = value

    # Add popped keys back in
    d.update(nd)