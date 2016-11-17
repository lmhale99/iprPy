#!/usr/bin/env python

#Standard library imports
import os
import sys
import uuid
import shutil

#http://www.numpy.org/
import numpy as np

#https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

calc_name = 'grain_boundary'

def main(*args):

    with open(args[0]) as f:
        prepare_dict = read_variable_script(f)
        
    #Load all records that match conditions
    records = iprPy.prepare.read_records(prepare_dict['lib_directory'], 
                                         calc_type='refine_structure', 
                                         potential=prepare_dict['potential_name'], 
                                         prototype='A2--W--bcc')


    for record in records:
        
        #Skip if strain range not 1e-6
        strain_range = record['model'].find('strain-range')
        if not np.isclose(strain_range, 1e-6): continue
        
        #Load potential listed in record
        potential_name = record['model'].find('potential')['id']
        potential = iprPy.prepare.read_lammps_potentials(prepare_dict['potential_directory'], name=potential_name)
        assert len(potential) == 1
        potential = potential[0]
        
        #Load symbols
        symbols = record['model'].find('system-info')['symbols']
        symbols_name = '-'.join(iprPy.tools.as_list(symbols))
        
        #Load prototype_name (i.e. system family)
        prototype_name = record['model'].find('system-info')['artifact']['family']
        
        #Load cohesive energy
        try:
            E_coh = uc.value_unit(record['model'].find('cohesive-energy'))
        except:
            continue
        
        #Load lattice parameter
        alat = uc.value_unit(record['model'].find('relaxed-atomic-system').find('a'))
        
        #Define record_directory in library
        record_directory = os.path.join(prepare_dict['lib_directory'], potential_name, symbols_name, prototype_name, calc_name)
        
        #Loop over grain boundaries
        for x_axis_1, y_axis_1, z_axis_1, x_axis_2, y_axis_2, z_axis_2 in zip(prepare_dict['x_axis_1'], 
                                                                              prepare_dict['y_axis_1'], 
                                                                              prepare_dict['z_axis_1'], 
                                                                              prepare_dict['x_axis_2'], 
                                                                              prepare_dict['y_axis_2'], 
                                                                              prepare_dict['z_axis_2']):
            
            #Create calc_id
            calc_id = str(uuid.uuid4())
        
            #parameter conversions
            v1 = np.array(x_axis_1.strip().split(), dtype=float)
            v2 = np.array(x_axis_2.strip().split(), dtype=float)
        
            #Define values for incomplete record
            record_dict = {}
            record_dict['uuid'] =                  calc_id
            record_dict['gb_angle'] =              am.tools.vect_angle(v1, v2)
            record_dict['x_step_size'] =           uc.set_literal(prepare_dict['x_step_size'])
            record_dict['z_step_size'] =           uc.set_literal(prepare_dict['z_step_size'])
            record_dict['potential_model'] =       potential['model']
            record_dict['system_family'] =         prototype_name
            record_dict['symbols'] =               iprPy.tools.as_list(symbols) * 3
            record_dict['x-axis_1'] =              list(np.array(x_axis_1.split(), dtype=int))
            record_dict['y-axis_1'] =              list(np.array(y_axis_1.split(), dtype=int))
            record_dict['z-axis_1'] =              list(np.array(z_axis_1.split(), dtype=int))
            record_dict['x-axis_2'] =              list(np.array(x_axis_2.split(), dtype=int))
            record_dict['y-axis_2'] =              list(np.array(y_axis_2.split(), dtype=int))
            record_dict['z-axis_2'] =              list(np.array(z_axis_2.split(), dtype=int))
            record_dict['length_unit'] =           prepare_dict['length_unit']
            
            #Create incomplete record and save to record_directory
            new_record = iprPy.calculation_data_model(calc_name, record_dict)
            try:
                with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
                    new_record.xml(fp=f, indent=2)
            except:
                os.makedirs(record_directory)
                with open(os.path.join(record_directory, calc_id + '.xml'), 'w') as f:
                    new_record.xml(fp=f, indent=2)
                  
            #Generate calculation folder    
            calc_directory = os.path.join(prepare_dict['run_directory'], calc_id)
            os.makedirs(calc_directory)
            
            #Define values for calc_*.in file
            calculation_dict = {}
            calculation_dict['lammps_command'] =   prepare_dict['lammps_command']
            calculation_dict['mpi_command'] =      prepare_dict['mpi_command']
            calculation_dict['potential_file'] =   potential['file']
            calculation_dict['potential_dir'] =    potential['dir']
            calculation_dict['symbols'] =          ' '.join(iprPy.tools.as_list(symbols) * 3)
            calculation_dict['alat'] =             alat
            calculation_dict['E_coh'] =            E_coh
            calculation_dict['x-axis_1'] =         x_axis_1
            calculation_dict['y-axis_1'] =         y_axis_1
            calculation_dict['z-axis_1'] =         z_axis_1
            calculation_dict['x-axis_2'] =         x_axis_2
            calculation_dict['y-axis_2'] =         y_axis_2
            calculation_dict['z-axis_2'] =         z_axis_2
            calculation_dict['x_step_size'] =      prepare_dict['x_step_size']
            calculation_dict['z_step_size'] =      prepare_dict['z_step_size']
            calculation_dict['length_unit'] =      prepare_dict['length_unit']
            calculation_dict['pressure_unit'] =    prepare_dict['pressure_unit']
            calculation_dict['energy_unit'] =      prepare_dict['energy_unit']
            calculation_dict['force_unit'] =       prepare_dict['force_unit']

            #Create calc_*.in by filling in calculation's template
            template = iprPy.calculation_template(calc_name)
            calc_in = iprPy.tools.fill_template(template, calculation_dict, '<', '>')
            with open(os.path.join(calc_directory, 'calc_' + calc_name + '.in'), 'w') as f:
                f.write('\n'.join(calc_in))
            
            #Copy calculation files
            for calc_file in iprPy.calculation_files(calc_name):
                shutil.copy(calc_file, calc_directory)      


                
def read_variable_script(f):
    """Read the given variable script, make assertions and assign default values to key terms"""
    
    prepare_dict = iprPy.prepare.read_variable_script(f)
    
    #Assign default values
    prepare_dict['mpi_command'] =           prepare_dict.get('mpi_command',     '')
    prepare_dict['potential_name'] =        prepare_dict.get('potential_name',  ['*'])
    prepare_dict['length_unit'] =           prepare_dict.get('length_unit',     '')
    prepare_dict['pressure_unit'] =         prepare_dict.get('pressure_unit',   '')
    prepare_dict['energy_unit'] =           prepare_dict.get('energy_unit',     '')
    prepare_dict['force_unit'] =            prepare_dict.get('force_unit',      '')
    
    #Check singular terms
    for key in singular_keys():
        assert not isinstance(prepare_dict[key], list)

    #Check multiple terms
    prepare_dict['x_axis_1'] = iprPy.tools.as_list(prepare_dict['x_axis_1'])
    prepare_dict['y_axis_1'] = iprPy.tools.as_list(prepare_dict['y_axis_1'])
    prepare_dict['z_axis_1'] = iprPy.tools.as_list(prepare_dict['z_axis_1'])
    prepare_dict['x_axis_2'] = iprPy.tools.as_list(prepare_dict['x_axis_2'])
    prepare_dict['y_axis_2'] = iprPy.tools.as_list(prepare_dict['y_axis_2'])
    prepare_dict['z_axis_2'] = iprPy.tools.as_list(prepare_dict['z_axis_2'])
    
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['y_axis_1'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['z_axis_1'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['x_axis_2'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['y_axis_2'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['z_axis_2'])
    
    return prepare_dict
    
def singular_keys():
    return ['run_directory', 
            'lib_directory',
            'lammps_command',
            'mpi_command',
            'potential_directory',
            'x_step_size',
            'z_step_size',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit']

                
if __name__ == '__main__':
    main(*sys.argv[1:])              