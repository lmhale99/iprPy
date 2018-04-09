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
            
            'load_file',
            'load_options',
            'symbols',
            
            'potential_LAMMPS_key',
            
            'a_mult',
            'b_mult',
            'c_mult',
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
            'temperature',
            'pressure_xx',
            'pressure_yy',
            'pressure_zz',
           ]