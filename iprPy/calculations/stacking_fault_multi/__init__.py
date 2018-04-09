# Standard Python libraries
from __future__ import division, absolute_import, print_function
import os
import importlib

##############################################################
# NOTE: file_names in files() are unique to each calculation! #
##############################################################

__all__ = ['prepare', 'process_input', 'template', 'files']

# Extract and define calculation file information
calc_dir = os.path.dirname(os.path.abspath(__file__))
calc_type = os.path.basename(calc_dir)
calc_name = 'calc_' + calc_type
prepare_name = 'prepare_' + calc_type

# Load read_input from calc_*.py script
calc = importlib.import_module('.'+calc_name, __name__)
process_input = calc.process_input

# Load prepare and prepare_keys from prepare_*.py script
prep = importlib.import_module('.'+prepare_name, __name__)
prepare = prep.prepare
prepare_keys = {'singular': prep.singularkeys(),
                'multi': prep.multikeys()}

# Define template function
def template():
    """
    The template to use for generating calc.in files.
    
    Returns
    -------
    str
        The contents of the template file.
    """
    with open(os.path.join(calc_dir, calc_name+'.template')) as template_file:
        return template_file.read()

# Define files function
def files():
    """
    All files required to perform the calculation.
    
    Yields
    ------
    str
        The absolute file paths of the required calculation files.
    """
    file_names = [
                  calc_name+'.py',
                  'sfmin.template',
                 ]
    
    for file_name in file_names:
        yield os.path.join(calc_dir, file_name)