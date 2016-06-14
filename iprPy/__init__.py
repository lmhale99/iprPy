import calculations
import prepare_functions
import tools

def calculation_names():
    """Returns a list of the names of the loaded calculations."""
    return calculations.calc.keys()
    
def prepare_function_names():
    """Returns a list of the names of the loaded prepare functions."""
    return prepare_functions.funct.keys()

def prepare_function(name, terms, variables):
    """Calls the prepare function with the given module name."""
    try:
        funct = prepare_functions.funct[name]
    except:
        raise KeyError('No prepare function ' + name + ' imported')
    try:
        funct_prepare = funct.prepare
    except:
        raise AttributeError('Prepare function ' + name + ' has no attribute prepare')    
    
    return funct_prepare(terms, variables)    
    
def calculation_prepare(name, terms, variables):
    """Calls the prepare function for the named calculation."""
    try:
        calc = calculations.calc[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')
    try:
        calc_prepare = calc.prepare
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute prepare') 
    
    return calc_prepare(terms, variables)
    
def calculation_data_model(name, input_dict, results_dict):
    """Generates a data model for the named calculation."""
    try:
        calc = calculations.calc[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')
    try:
        calc_data_model = calc.data_model
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute data_model') 
    
    return calc_data_model(input_dict, results_dict)
    
def calculation_read_input(name, fp, *args):
    """Reads the calc_*.in input commands for the named calculation."""
    try:
        calc = calculations.calc[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')
    try:
        calc_read_input = calc.read_input
    except:
        raise AttributeError('Calculation ' + name + ' has no attribute read_input') 
    
    return calc_read_input(fp, *args)    