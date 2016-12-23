#!/usr/bin/env python

#Standard library imports
import os
import sys
import glob
import shutil
import uuid

#http://www.numpy.org/
import numpy as np

#https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_type__ = 'E_vs_r_scan'

def main(*args):
    with open(args[0]) as f:
        prepare_dict = read_variable_script(f)

    #Load potentials and prototypes
    potentials = iprPy.prepare.read_lammps_potentials(prepare_dict['potential_directory'],
                                                      element=prepare_dict['element_name'],
                                                      name=prepare_dict['potential_name'])
    prototypes = iprPy.prepare.read_prototypes(prepare_dict['prototype_directory'], 
                                               natypes=prepare_dict['number_atypes'],
                                               name=prepare_dict['prototype_name'])

    #Iterate over all combinations of potentials, prototypes and symbols
    for potential, prototype, symbols in iprPy.prepare.all_prototype_combos(potentials, prototypes):    
        potential_name = os.path.basename(potential['dir'])
        prototype_name = os.path.splitext(os.path.basename(prototype['file']))[0]
        symbols_name = '-'.join(symbols)
        
        #Define record_directory in library
        record_directory = os.path.join(prepare_dict['lib_directory'], potential_name, symbols_name, prototype_name, __calc_type__)
        
        #Create calc_id
        calc_id = str(uuid.uuid4())
        
        #parameter conversions
        size_mults_array = iprPy.input.parse_size_mults(prepare_dict)
        
        #Define values for incomplete record
        record_dict = {}
        record_dict['uuid'] =                  calc_id
        record_dict['size_mults'] =            size_mults_array
        record_dict['minimum_r'] =             uc.set_literal(prepare_dict['minimum_r'])
        record_dict['maximum_r'] =             uc.set_literal(prepare_dict['maximum_r'])
        record_dict['number_of_steps_r'] =     int(prepare_dict['number_of_steps_r'])
        record_dict['potential_model'] =       potential['model']
        record_dict['load'] =                  'system_model ' + prototype['file']
        record_dict['system_family'] =         prototype_name
        record_dict['symbols'] =               symbols
        record_dict['length_unit'] =           prepare_dict['length_unit']
        
        #Create incomplete record and save to record_directory
        new_record = iprPy.calculation_data_model(__calc_type__, record_dict)
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
        calculation_dict['load'] =             'system_model ' + prototype['file']
        calculation_dict['load_options'] =     ''
        calculation_dict['symbols'] =          ' '.join(symbols)
        calculation_dict['box_parameters'] =   ''
        calculation_dict['x-axis'] =           ''
        calculation_dict['y-axis'] =           ''
        calculation_dict['z-axis'] =           ''
        calculation_dict['shift'] =            ''
        calculation_dict['size_mults'] =       prepare_dict['size_mults']
        calculation_dict['length_unit'] =      prepare_dict['length_unit']
        calculation_dict['pressure_unit'] =    prepare_dict['pressure_unit']
        calculation_dict['energy_unit'] =      prepare_dict['energy_unit']
        calculation_dict['force_unit'] =       prepare_dict['force_unit']
        calculation_dict['minimum_r'] =        prepare_dict['minimum_r']
        calculation_dict['maximum_r'] =        prepare_dict['maximum_r']
        calculation_dict['number_of_steps_r']= prepare_dict['number_of_steps_r']
        
        #Create calc_*.in by filling in calculation's template
        template = iprPy.calculation_template(__calc_type__)
        calc_in = iprPy.tools.fill_template(template, calculation_dict, '<', '>')
        with open(os.path.join(calc_directory, 'calc_' + __calc_type__ + '.in'), 'w') as f:
            f.write('\n'.join(calc_in))
        
        #Copy calculation files
        for calc_file in iprPy.calculation_files(__calc_type__):
            shutil.copy(calc_file, calc_directory)          
        
def read_variable_script(f):
    """Read the given variable script, make assertions and assign default values to key terms"""
    
    prepare_dict = iprPy.prepare.read_variable_script(f)
    
    #Assign default values
    prepare_dict['mpi_command'] =       prepare_dict.get('mpi_command',       '')
    prepare_dict['potential_name'] =    prepare_dict.get('potential_name',    None)
    prepare_dict['element_name'] =      prepare_dict.get('element_name',      None)
    prepare_dict['prototype_name'] =    prepare_dict.get('prototype_name',    None)
    prepare_dict['number_atypes'] =     prepare_dict.get('number_atypes',     None)
    prepare_dict['length_unit'] =       prepare_dict.get('length_unit',       'angstrom')
    prepare_dict['pressure_unit'] =     prepare_dict.get('pressure_unit',     'GPa')
    prepare_dict['energy_unit'] =       prepare_dict.get('energy_unit',       'eV')
    prepare_dict['force_unit'] =        prepare_dict.get('force_unit',        'eV/angstrom')
    prepare_dict['size_mults'] =        prepare_dict.get('size_mults',        '0 3 0 3 0 3')
    prepare_dict['minimum_r'] =         prepare_dict.get('minimum_r',         '2 angstrom')
    prepare_dict['maximum_r'] =         prepare_dict.get('maximum_r',         '6 angstrom')
    prepare_dict['number_of_steps_r'] = prepare_dict.get('number_of_steps_r', '200')
    
    #Check singular terms
    for key in singular_keys():
        assert not isinstance(prepare_dict[key], list)

    #Check multiple terms
    #None for this calculation
    
    return prepare_dict
    
def singular_keys():
    return ['run_directory', 
            'lib_directory',
            'lammps_command',
            'mpi_command',
            'potential_directory',
            'prototype_directory',
            'size_mults',
            'minimum_r',
            'maximum_r',
            'number_of_steps_r',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit']
            
if __name__ == '__main__':
    main(*sys.argv[1:])     