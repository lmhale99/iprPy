def boolean(value):
    """Allows conversion of strings to Booleans"""
    
    #Pass Boolean values through without changing
    if value is True:    return True
    elif value is False: return False
    
    #Convert strings
    elif value.lower() in ['true', 't']:  return True
    elif value.lower() in ['false', 'f']: return False
    
    #Issue error for invalid string
    else: raise ValueError('Invalid Boolean string')
