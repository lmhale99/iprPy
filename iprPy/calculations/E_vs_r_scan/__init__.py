import os
import importlib

##############################################################
# NOTE: file_names in files() are unique to each calculation! #
##############################################################

#Extract and define calculation file information
calc_dir = os.path.dirname(os.path.abspath(__file__))
calc_type = os.path.basename(calc_dir)
calc_name = 'calc_' + calc_type
prepare_name = 'prepare_' + calc_type

#Load data_model and read_input from calc_*.py script
calc = importlib.import_module('.'+calc_name, __name__)
data_model = calc.data_model
read_input = calc.read_input

#Load prepare and prepare_keys from prepare_*.py script
try:
    prep = importlib.import_module('.'+prepare_name, __name__)
    prepare = prep.prepare
    prepare_keys = {'singular': prep.singularkeys(),
                    'multi': prep.multikeys()}
except:
    pass

#Define template function
def template():
    """Returns the contents of the calculation's input parameter template file"""
    with open(os.path.join(calc_dir, calc_name+'.template')) as template_file:
        return template_file.read()

#Define files function
def files():
    """Yields all files necessary to the calculation"""
    file_names = [calc_name+'.py',
                  'run0.template']
                      
    for i in xrange(len(file_names)):
        yield os.path.join(calc_dir, file_names[i])

