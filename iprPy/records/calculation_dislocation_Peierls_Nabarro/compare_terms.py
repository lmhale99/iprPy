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
            
            'xnum',
            
            'load_file',
            'load_options',
            'symbols',
            
            'dislocation_key',
            'gammasurface_calc_key',
            
            'cdiffelastic'
            'cdiffgradient'
            'cdiffstress',
            
            'fullstress',
            'min_method',
            'min_options',
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
            'xmax',
            'xstep',
            'cutofflongrange',
            'K11', 'K12', 'K13', 'K22', 'K23', 'K33',
            'tau11', 'tau12', 'tau13', 'tau22', 'tau23', 'tau33',
            'beta11', 'beta12', 'beta13', 'beta22', 'beta23', 'beta33',
            'alpha1',
           ]