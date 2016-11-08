import os
import glob
import iprPy
import shutil
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
import numpy as np
import uuid

#Input values (to be moved later)
run_directory =         'C:/Users/lmh1/Documents/calculations/ipr/torun/1'
lib_directory =         'C:/Users/lmh1/Documents/calculations/ipr/library_2016_10_26'
lammps_command =        'lmp_serial'
mpi_command =           ''

potential_directory =   'C:/Users/lmh1/Documents/Python-packages/iprPy/reference-libraries/potentials'
prototype_directory =   'C:/Users/lmh1/Documents/Python-packages/iprPy/reference-libraries/prototypes'
            
size_mults =            '0 3 0 3 0 3'
size_mults_array =      np.array([[0, 3], [0, 3],[0, 3]])

length_unit =           'angstrom'
pressure_unit =         'GPa'
energy_unit =           'eV'
force_unit =            'eV/angstrom'

minimum_r =             2.0
maximum_r =             6.0
number_of_steps_r =     100

calc_name = 'E_vs_r_scan'

#Get input template
template_path = 'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/E_vs_r_scan/calc_files/calc_E_vs_r_scan.template'
with open(template_path) as template_file:
    template = template_file.read()

#Get files to copy to each calc folder
calc_files = ['C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/E_vs_r_scan/calc_files/calc_E_vs_r_scan.py',
              'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/E_vs_r_scan/calc_files/run0.template']
    
#Load potentials and prototypes
potentials = iprPy.prepare.read_lammps_potentials(potential_directory)
prototypes = iprPy.prepare.read_prototypes(prototype_directory)

#Iterate over all combinations of potentials, prototypes and symbols
for potential, prototype, symbols in iprPy.prepare.all_prototype_combos(potentials, prototypes):    
    potential_name = os.path.basename(potential['dir'])
    prototype_name = os.path.splitext(os.path.basename(prototype['file']))[0]
    symbols_name = '-'.join(symbols)
    
    #Create calc_id
    calc_id = str(uuid.uuid4())
    
    #Generate library record
    record_directory = os.path.join(lib_directory, potential_name, symbols_name, prototype_name, calc_name)
    
    record_variables = {}
    record_variables['uuid'] =                  calc_id
    record_variables['size_mults'] =            size_mults_array
    record_variables['minimum_r'] =             minimum_r
    record_variables['maximum_r'] =             maximum_r
    record_variables['number_of_steps_r'] =     number_of_steps_r
    record_variables['potential'] =             potential['model']
    record_variables['load'] =                  'system_model ' + prototype['file']
    record_variables['system_family'] =         prototype_name
    record_variables['symbols'] =               symbols
    
    record = iprPy.calculation_data_model(calc_name, record_variables)
    try:
        with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
            record.xml(fp=f, indent=2)
    except:
        os.makedirs(record_directory)
        with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
            record.xml(fp=f, indent=2)
    
    #Generate calculation folder    
    calc_directory = os.path.join(run_directory, calc_id)
    os.makedirs(calc_directory)
    
    calculation_variables = {}
    calculation_variables['lammps_command'] =   lammps_command
    calculation_variables['mpi_command'] =      mpi_command
    calculation_variables['potential_file'] =   potential['file']
    calculation_variables['potential_dir'] =    potential['dir']
    calculation_variables['load'] =             'system_model ' + prototype['file']
    calculation_variables['load_options'] =     ''
    calculation_variables['symbols'] =          ' '.join(symbols)
    calculation_variables['box_parameters'] =   ''
    calculation_variables['x-axis'] =           ''
    calculation_variables['y-axis'] =           ''
    calculation_variables['z-axis'] =           ''
    calculation_variables['shift'] =            ''
    calculation_variables['size_mults'] =       size_mults
    calculation_variables['length_unit'] =      length_unit
    calculation_variables['pressure_unit'] =    pressure_unit
    calculation_variables['energy_unit'] =      energy_unit
    calculation_variables['force_unit'] =       force_unit
    calculation_variables['minimum_r'] =        str(minimum_r)
    calculation_variables['maximum_r'] =        str(maximum_r)
    calculation_variables['number_of_steps_r']= str(number_of_steps_r)
    
    calc_in = iprPy.tools.fill_template(template, calculation_variables, '<', '>')
    with open(os.path.join(calc_directory, 'calc_' + calc_name + '.in'), 'w') as f:
        f.write('\n'.join(calc_in))
        
    for calc_file in iprPy.prepare.as_list(calc_files):
        shutil.copy(calc_file, calc_directory)    