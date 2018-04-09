# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

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
            
            'tausteps',
            'cdiffstress',
            'fullstress',
            'min_method',
            'min_options',
            'load_file',
            'load_options',
            'symbols',
            
            'dislocation_key',
            'gammasurface_calc_key',
            'peierlsnabarro_calc_key',
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
            'delta_tau_xy',
            'delta_tau_yy',
            'delta_tau_yz',
           ]