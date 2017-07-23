from __future__ import division, absolute_import, print_function

def compare_terms():
    """
    The default terms used by isnew() for exact, i.e. ==, comparisons.
    
    Returns
    -------
    list of str
        The names of the terms to use for direct comparisons.
    """
    return [
            'calc_script',
            
            'load_file',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult1',
            'a_mult2',
            'b_mult1',
            'b_mult2',
            'c_mult1',
            'c_mult2',
            
            'dislocation_key',
           ]

def compare_fterms():
    """
    The default terms used by isnew() for approximate, i.e. numpy.isclose,
    comparisons.
    
    Returns
    -------
    list of str
        The names of the terms to use for approximate comparisons.
    """
    return [
            'annealtemperature',
           ]