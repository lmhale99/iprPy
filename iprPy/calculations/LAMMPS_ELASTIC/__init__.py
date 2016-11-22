import os
from calc_LAMMPS_ELASTIC import data_model, read_input

__calc_dir__ = os.path.dirname(os.path.abspath(__file__))
__calc_type__ = os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def template():
    with open(os.path.join(__calc_dir__, __calc_name__+'.template')) as template_file:
        return template_file.read()

def files():
    file_names = [__calc_name__+'.py',
                  'displace.mod',
                  'in.elastic',
                  'init.mod.template',
                  'potential.mod.template']
                      
    for i in xrange(len(file_names)):
        yield os.path.join(__calc_dir__, file_names[i])

