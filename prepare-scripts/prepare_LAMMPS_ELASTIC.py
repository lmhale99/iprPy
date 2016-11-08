import os
import glob

import atomman as am
import atomman.lammps as lmp

import numpy as np
import iprPy
import uuid
import shutil

#Input values (to be moved later)
run_directory =         'C:/Users/lmh1/Documents/calculations/ipr/torun/1'
lib_directory =         'C:/Users/lmh1/Documents/calculations/ipr/library_2016_10_26'
lammps_command =        'lmp_serial'
mpi_command =           ''

potential_directory =   'C:/Users/lmh1/Documents/Python-packages/iprPy/reference-libraries/potentials'
            
size_mults =            '0 3 0 3 0 3'
size_mults_array =      np.array([[0, 3], [0, 3],[0, 3]])

length_unit =           'angstrom'
pressure_unit =         'GPa'
energy_unit =           'eV'
force_unit =            'eV/angstrom'

energy_tolerance =      ''
force_tolerance =       ''
maximum_iterations =    ''
maximum_evaluations =   ''
maximum_atomic_motion = ''

strain_range =          [1e-4, 1e-5, 1e-6, 1e-7, 1e-8]

calc_name = 'LAMMPS_ELASTIC'

#Get input template
template_path = 'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/calc_LAMMPS_ELASTIC.template'
with open(template_path) as template_file:
    template = template_file.read()

#Get files to copy to each calc folder
calc_files = ['C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/calc_LAMMPS_ELASTIC.py',
              'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/in.elastic',
              'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/displace.mod',
              'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/init.mod.template',
              'C:/Users/lmh1/Documents/Python-packages/iprPy/iprPy/calculations/LAMMPS_ELASTIC/calc_files/potential.mod.template']
    
#Load records    
records = iprPy.prepare.read_records(lib_directory, calc_type='E_vs_r_scan')

for record in records:
    
    #Load potential
    potential_name = record['model'].find('potential')['id']
    potential = iprPy.prepare.read_lammps_potentials(potential_directory, name=potential_name)
    assert len(potential) == 1
    potential = potential[0]
    
    #Load symbols
    symbols = record['model'].find('system-info')['symbols']
    symbols_name = '-'.join(iprPy.prepare.as_list(symbols))
    
    #Load prototype_name (i.e. system family)
    prototype_name = record['model'].find('system-info')['artifact']['family']
    
    #Define record_directory in library
    record_directory = os.path.join(lib_directory, potential_name, symbols_name, prototype_name, calc_name)
    
    #Loop over atomic-systems in record
    for i in xrange(len(record['model'].finds('minimum-atomic-system'))):    
        if i == 0:
            load_options = 'key minimum-atomic-system'
        else:
            load_options = 'key minimum-atomic-system index '+str(i)
        
        #Loop over strain_ranges
        for strain in iprPy.prepare.iter_as_list(strain_range):
            
            #Create calc_id
            calc_id = str(uuid.uuid4())
        
            #Generate library record
            record_directory = os.path.join(lib_directory, potential_name, symbols_name, prototype_name, calc_name)
            
            record_variables = {}
            record_variables['uuid'] =                  calc_id
            record_variables['strain_range'] =          strain
            record_variables['size_mults'] =            size_mults_array
            record_variables['potential_model'] =       potential['model']
            record_variables['load'] =                  'system_model ' + record['file']
            record_variables['load_options'] =          load_options
            record_variables['system_family'] =         prototype_name
            record_variables['symbols'] =               symbols
            record_variables['pressure_unit'] =         pressure_unit
            
            new_record = iprPy.calculation_data_model(calc_name, record_variables)
            try:
                with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
                    new_record.xml(fp=f, indent=2)
            except:
                os.makedirs(record_directory)
                with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
                    new_record.xml(fp=f, indent=2)
            
            #Generate calculation folder    
            calc_directory = os.path.join(run_directory, calc_id)
            os.makedirs(calc_directory)
            
            calculation_variables = {}
            calculation_variables['lammps_command'] =   lammps_command
            calculation_variables['mpi_command'] =      mpi_command
            calculation_variables['potential_file'] =   potential['file']
            calculation_variables['potential_dir'] =    potential['dir']
            calculation_variables['load'] =             'system_model ' + record['file']
            calculation_variables['load_options'] =     load_options
            calculation_variables['symbols'] =          ''
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
            calculation_variables['strain_range'] =     strain
            calculation_variables['energy_tolerance'] = energy_tolerance
            calculation_variables['force_tolerance'] =  force_tolerance
            calculation_variables['maximum_iterations'] =   maximum_iterations
            calculation_variables['maximum_evaluations']=   maximum_evaluations
            calculation_variables['maximum_atomic_motion']= maximum_atomic_motion
            
            calc_in = iprPy.tools.fill_template(template, calculation_variables, '<', '>')
            with open(os.path.join(calc_directory, 'calc_' + calc_name + '.in'), 'w') as f:
                f.write('\n'.join(calc_in))
                
            for calc_file in iprPy.prepare.as_list(calc_files):
                shutil.copy(calc_file, calc_directory)
            
        