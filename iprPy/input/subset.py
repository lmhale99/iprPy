from .subset_classes import loaded

def subset(style, prefix=''):
    """
    Wrapper function for the modular subset styles

    Parameters
    ----------
    style : str
        The subset style to access
    prefix : str, optional
        The prefix to add to all keys of the subset
    
    Returns
    -------
    iprPy.input.subset_classes.Subset subclass
    """
    return loaded[style](prefix=prefix)