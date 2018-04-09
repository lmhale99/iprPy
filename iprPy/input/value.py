# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

def value(input_dict, key, default_unit=None, default_term=None):
    """
    Interprets a calculation parameter by converting it from a string to a
    float in working units.
        
    The parameter being converted is a str with one of two formats:
    - '<number>'
    - '<number> <unit>'
    
    Parameters
    ----------
    input_dict : dict
        Dictionary containing input parameter key-value pairs.
    key : str
        The key of input_dict to evaluate.
    default_unit : str, optional
        Default unit to use if not specified in the parameter value.  If not
        given, then no unit conversion will be done on unitless parameter
        values.
    default_term : str, optional
        Default str parameter value to use if key not in input_dict.  Can be
        specified as '<value> <unit>' to ensure that the default value is 
        always the same regardless of the working units or default_unit.  If
        not given, then key must be in input_dict.
    
    Returns
    -------
    float
        The interpreted value of the input parameter's str value in the
        working units.
    """
    term = input_dict.get(key, default_term)
    
    try:
        i = term.strip().index(' ')
        value = float(term[:i])
        unit = term[i+1:]
    except:
        value = float(term)
        unit = default_unit
    
    return uc.set_in_units(value, unit)