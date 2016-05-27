import calculations
import tools

def calc_names():
    return calculations.calc.keys()

def prepare(name, terms, variables):
    try:
        calc = calculations.calc[name]
    except:
        raise KeyError('No calculation ' + name + ' imported')
    return calculations.calc[name].prepare(terms, variables)
    
def process(name, *args, **kwargs):
    return calculations.calc[name].process(*args, **kwargs)