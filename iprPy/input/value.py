import atomman.unitconvert as uc

def value(input_dict, key, default_unit=None, default_term=None):
    """
    Converts a string dictionary value into a float with proper unit conversion.
    
    The string can either be:
        a number
        a number and unit separated by a single space
    
    Keyword Arguments:
    input_dict -- a dictionary
    key -- the key for the value in input_dict
    default_unit -- unit for the value if not specified in the string.
    default_term -- string of the value (and unit) to use if key is not in input_dict.
    
    Note that the unit in default_term does not have to correspond to default_unit.
    This allows for default values to be constant regardless of preferred units.
    
    returns the value as a float in atomman's working units.
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