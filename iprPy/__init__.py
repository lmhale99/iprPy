import tools
import input
import prepare
import calculations

def calculation_names():
    """Returns a list of the names of the loaded calculations."""
    return calculations.calc.keys()
    
def calculation_data_model(name, input_dict, results_dict=None):
    """Generates a data model for the named calculation."""
    
    calc = get_calculation(name)
    try: calc_data_model = calc.data_model
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute data_model') 
    
    return calc_data_model(input_dict, results_dict)
    
def calculation_read_input(name, fp, *args):
    """Reads the calc_*.in input commands for the named calculation."""
    
    calc = get_calculation(name)
    try: calc_read_input = calc.read_input
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute read_input') 
    
    return calc_read_input(fp, *args)   

def calculation_template(name):
    """Reads the calc_*.in input commands for the named calculation."""
    
    calc = get_calculation(name)
    try: calc_template = calc.template
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute template') 
    
    return calc_template()

def calculation_files(name):
    """Yields the list of files necessary for a calculation to run"""
    
    calc = get_calculation(name)
    try: calc_files = calc.files
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute files') 
    
    return calc_files()
    
def get_calculation(name):
    """Returns calculation module if it exists"""
    try:
        return calculations.calc[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')