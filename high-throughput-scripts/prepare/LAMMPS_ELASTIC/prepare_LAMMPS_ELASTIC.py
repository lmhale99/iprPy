#!/usr/bin/env python

#Standard library imports
import os
import sys
import glob
import uuid
import shutil

#http://www.numpy.org/
import numpy as np

#https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_type__ = 'LAMMPS_ELASTIC'

def main(*args):
    with open(args[0]) as f:
        prepare_dict = read_variable_script(f)

    #Load E_vs_r_scan records
    records = iprPy.prepare.read_records(prepare_dict['lib_directory'], 
                                         calc_type='E_vs_r_scan', 
                                         potential=prepare_dict['potential_name'], 
                                         symbols=  prepare_dict['symbol_name'], 
                                         prototype=prepare_dict['prototype_name'])

    for record in records:
    
        #Load potential
        potential_name = record['model'].find('potential')['id']
        potential = iprPy.prepare.read_lammps_potentials(prepare_dict['potential_directory'], name=potential_name)
        assert len(potential) == 1
        potential = potential[0]
        
        #Load symbols
        symbols = record['model'].find('system-info')['symbols']
        symbols_name = '-'.join(iprPy.tools.as_list(symbols))
        
        #Load prototype_name (i.e. system family)
        prototype_name = record['model'].find('system-info')['artifact']['family']
        
        #Define record_directory in library
        record_directory = os.path.join(prepare_dict['lib_directory'], potential_name, symbols_name, prototype_name, __calc_type__)
        
        #Loop over atomic-systems in record
        for i in xrange(len(record['model'].finds('minimum-atomic-system'))):    
            if i == 0:
                load_options = 'key minimum-atomic-system'
            else:
                load_options = 'key minimum-atomic-system index '+str(i)
            
            #Loop over strain_ranges
            for strain in iprPy.tools.iter_as_list(prepare_dict['strain_range']):
                
                #Generate library record
                record_directory = os.path.join(prepare_dict['lib_directory'], potential_name, symbols_name, prototype_name, __calc_type__)
                
                #Create calc_id
                calc_id = str(uuid.uuid4())
                
                #parameter conversions
                size_mults_array = iprPy.input.parse_size_mults(prepare_dict)
                
                record_dict = {}
                record_dict['uuid'] =                  calc_id
                record_dict['strain_range'] =          strain
                record_dict['size_mults'] =            size_mults_array
                record_dict['potential_model'] =       potential['model']
                record_dict['load'] =                  'system_model ' + record['file']
                record_dict['load_options'] =          load_options
                record_dict['system_family'] =         prototype_name
                record_dict['symbols'] =               symbols
                record_dict['pressure_unit'] =         prepare_dict['pressure_unit']
                
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
                
                calculation_dict = {}
                calculation_dict['lammps_command'] =   prepare_dict['lammps_command']
                calculation_dict['mpi_command'] =      prepare_dict['mpi_command']
                calculation_dict['potential_file'] =   potential['file']
                calculation_dict['potential_dir'] =    potential['dir']
                calculation_dict['load'] =             'system_model ' + record['file']
                calculation_dict['load_options'] =     load_options
                calculation_dict['symbols'] =          ''
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
                calculation_dict['strain_range'] =     strain
                calculation_dict['energy_tolerance'] = prepare_dict['energy_tolerance']
                calculation_dict['force_tolerance'] =  prepare_dict['force_tolerance']
                calculation_dict['maximum_iterations'] =   prepare_dict['maximum_iterations']
                calculation_dict['maximum_evaluations']=   prepare_dict['maximum_evaluations']
                calculation_dict['maximum_atomic_motion']= prepare_dict['maximum_atomic_motion']
                
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
    prepare_dict['potential_name'] =    prepare_dict.get('potential_name',    ['*'])
    prepare_dict['symbol_name'] =       prepare_dict.get('symbol_name',       ['*'])
    prepare_dict['prototype_name'] =    prepare_dict.get('prototype_name',    ['*'])
    prepare_dict['length_unit'] =       prepare_dict.get('length_unit',       'angstrom')
    prepare_dict['pressure_unit'] =     prepare_dict.get('pressure_unit',     'GPa')
    prepare_dict['energy_unit'] =       prepare_dict.get('energy_unit',       'eV')
    prepare_dict['force_unit'] =        prepare_dict.get('force_unit',        'eV/angstrom')
    prepare_dict['size_mults'] =        prepare_dict.get('size_mults',        '0 3 0 3 0 3')
    prepare_dict['energy_tolerance'] =  prepare_dict.get('energy_tolerance',  '')
    prepare_dict['force_tolerance'] =   prepare_dict.get('force_tolerance',   '')
    prepare_dict['maximum_iterations'] = prepare_dict.get('maximum_iterations', '')
    prepare_dict['maximum_evaluations'] = prepare_dict.get('maximum_evaluations', '')
    prepare_dict['maximum_atomic_motion'] = prepare_dict.get('maximum_atomic_motion', '')
    prepare_dict['strain_range'] =      prepare_dict.get('strain_range',      '1e-6')
    
    #Check singular terms
    for key in singular_keys():
        assert not isinstance(prepare_dict[key], list)

    #Check multiple terms
    
    return prepare_dict
    
def singular_keys():
    return ['run_directory', 
            'lib_directory',
            'lammps_command',
            'mpi_command',
            'potential_directory',
            'size_mults',
            'energy_tolerance',
            'force_tolerance',
            'maximum_iterations',
            'maximum_evaluations',
            'maximum_atomic_motion',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit']
            
if __name__ == '__main__':
    main(*sys.argv[1:])                  
        