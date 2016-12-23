from .calculations import calculations_dict

#Utility functions
def calculation_names():
    """Returns a list of the names of the loaded calculations."""
    return calculations_dict.keys()
    
def get_calculation(name):
    """Returns calculation module if it exists"""
    try:
        return calculations_dict[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')
        
#Method specific functions        
def calculation_data_model(name, input_dict, results_dict=None):
    """Generates a data model for the named calculation."""
    
    calculation = get_calculation(name)
    try: data_model = calculation.data_model
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute data_model') 
    
    return data_model(input_dict, results_dict)
    
def calculation_read_input(name, fp, *args):
    """Reads the calc_*.in input commands for the named calculation."""
    
    calculation = get_calculation(name)
    try: read_input = calculation.read_input
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute read_input') 
    
    return read_input(fp, *args)   

def calculation_template(name):
    """Reads the calc_*.in input commands for the named calculation."""
    
    calculation = get_calculation(name)
    try: template = calculation.template
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute template') 
    
    return template()

def calculation_files(name):
    """Yields the list of files necessary for a calculation to run"""
    
    calculation = get_calculation(name)
    try: files = calculation.files
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute files') 
    
    return files()