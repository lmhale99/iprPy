__all__ = ['atomman_systemmanipulate']

def atomman_systemmanipulate():
    """
    Returns
    -------
    list
        The calculation input keys associated with manipulating an atomic
        atomman.System.

    """
    return  [
                'a_uvw',
                'b_uvw',
                'c_uvw',
                'atomshift',
                'sizemults',
            ]   