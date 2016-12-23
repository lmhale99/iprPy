#!/usr/bin/env python

#Standard library imports
import os
import sys
import glob
import shutil
import uuid

#http://www.numpy.org/
import numpy as np

#http://pandas.pydata.org/
import pandas as pd

#https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_type__ = 'E_vs_r_scan'
__record_type__ = 'calculation-cohesive-energy-relation'

def main(*args):
    with open(args[0]) as f:
        prepare_dict = read_variable_script(f)

    #open database
    dbase = iprPy.database_from_dict(prepare_dict)
    
    #Build record_df
    record_df = build_record_df(dbase, __record_type__)
        
    #Loop over all potentials
    for pot_id, pot_record, pot_archive in iprPy.prepare.yield_potentials(dbase,
                                                                          element =    prepare_dict['potential_element'],
                                                                          name =       prepare_dict['potential_name'],
                                                                          pair_style = prepare_dict['potential_pair_style']):
        potential = lmp.Potential(pot_record)
        
        #Loop over all prototypes
        for proto_id, proto_record in iprPy.prepare.yield_prototypes(dbase,
                                                                     natypes =        prepare_dict['prototype_natypes'], 
                                                                     name =           prepare_dict['prototype_name'], 
                                                                     space_group =    prepare_dict['prototype_space_group'], 
                                                                     crystal_family = prepare_dict['prototype_crystal_family'], 
                                                                     pearson =        prepare_dict['prototype_Pearson_symbol']):

            #Iterate over all combinations of potentials, prototypes and symbols
            for symbols in iprPy.prepare.yield_symbols_for_prototype(proto_record, potential):    
                
                #Create calc_key
                calc_key = str(uuid.uuid4())
                
                #parameter conversions
                size_mults_array = iprPy.input.parse_size_mults(prepare_dict)
                
                #Define values for incomplete record
                record_dict = {}
                record_dict['calc_key'] =              calc_key
                record_dict['size_mults'] =            size_mults_array
                record_dict['minimum_r'] =             uc.set_literal(prepare_dict['minimum_r'])
                record_dict['maximum_r'] =             uc.set_literal(prepare_dict['maximum_r'])
                record_dict['number_of_steps_r'] =     int(prepare_dict['number_of_steps_r'])
                record_dict['potential_key'] =         potential.key
                record_dict['potential_id'] =          potential.id
                record_dict['load'] =                  'system_model ' + proto_id+'.xml'
                record_dict['system_family'] =         proto_id
                record_dict['symbols'] =               symbols
                record_dict['length_unit'] =           prepare_dict['length_unit']
                
                #Create incomplete record and save to record_directory
                new_record = iprPy.calculation_data_model(__calc_type__, record_dict)
                if not is_new(record_df, new_record):
                    continue
                dbase.add_record(new_record.xml(), __record_type__, calc_key)
                
                #Generate calculation folder    
                calc_directory = os.path.join(prepare_dict['run_directory'], calc_key)
                os.makedirs(calc_directory)
                
                #Add files to calculation folder
                for calc_file in iprPy.calculation_files(__calc_type__):
                    shutil.copy(calc_file, calc_directory)  
                
                with open(os.path.join(calc_directory, pot_id+'.xml'), 'w') as f:
                    f.write(pot_record)
                pot_archive.extractall(calc_directory)
                with open(os.path.join(calc_directory, proto_id+'.xml'), 'w') as f:
                    f.write(proto_record)
                    
                #Define values for calc_*.in file
                calculation_dict = {}
                calculation_dict['lammps_command'] =   prepare_dict['lammps_command']
                calculation_dict['mpi_command'] =      prepare_dict['mpi_command']
                calculation_dict['potential_file'] =   pot_id + '.xml'
                calculation_dict['potential_dir'] =    pot_id
                calculation_dict['load'] =             'system_model ' + proto_id+'.xml'
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

def build_record_df(dbase, record_type):
    """Constructs a pandas.DataFrame for all records in a database of a given record_type"""
    df = []
    for record in dbase.iget_records(record_type):
        df.append(iprPy.record_to_dict(record, full=False))
    return pd.DataFrame(df)
    
def is_new(record_df, record):
    """Checks if a matching calculation record already exists"""
    
    if len(record_df) == 0:
        return True
    
    record_dict = iprPy.record_to_dict(record, full=False)

    #compare simple terms
    test_df = record_df[(record_df['calc_script'] ==       record_dict['calc_script']) &
                        (record_df['prototype'] ==         record_dict['prototype']) &
                        (record_df['number_of_steps_r'] == record_dict['number_of_steps_r']) &
                        (record_df['potential_id'] ==      record_dict['potential_id']) &
                        (record_df['potential_key'] ==     record_dict['potential_key']) &
                        (np.isclose(record_df['maximum_r'],record_dict['maximum_r'])) &
                        (np.isclose(record_df['minimum_r'],record_dict['minimum_r']))]

                        #Compare complex terms
    test = np.empty(len(test_df), dtype=bool)
    for i in xrange(len(test_df)):
        
        test[i] = (iprPy.tools.as_list(test_df.iloc[i].symbols) == iprPy.tools.as_list(record_dict['symbols']) and
                   np.all(test_df.iloc[i].size_mults == record_dict['size_mults']))

    test_df = test_df[test]
   
    if len(test_df) > 0:
        return False
    else:
        return True  
 
def read_variable_script(f):
    """Read the given variable script, make assertions and assign default values to key terms"""
    
    prepare_dict = iprPy.prepare.read_variable_script(f)
    
    #Assign default values
    prepare_dict['mpi_command'] = prepare_dict.get('mpi_command', '')
    
    prepare_dict['potential_name'] =       prepare_dict.get('potential_name',       None)
    prepare_dict['potential_element'] =    prepare_dict.get('potential_element',    None)
    prepare_dict['potential_pair_style'] = prepare_dict.get('potential_pair_style', None)
    
    prepare_dict['prototype_name'] =           prepare_dict.get('prototype_name',           None)
    prepare_dict['prototype_space_group'] =    prepare_dict.get('prototype_space_group',    None)
    prepare_dict['prototype_crystal_family'] = prepare_dict.get('prototype_crystal_family', None)
    prepare_dict['prototype_Pearson_symbol'] = prepare_dict.get('prototype_Pearson_symbol', None)
    prepare_dict['prototype_natypes'] =        prepare_dict.get('prototype_natypes',        None)
    
    prepare_dict['length_unit'] =   prepare_dict.get('length_unit',   'angstrom')
    prepare_dict['pressure_unit'] = prepare_dict.get('pressure_unit', 'GPa')
    prepare_dict['energy_unit'] =   prepare_dict.get('energy_unit',   'eV')
    prepare_dict['force_unit'] =    prepare_dict.get('force_unit',    'eV/angstrom')
    
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
    """List the prepare_*.in key terms that are restricted to having only one value."""
    return ['database', 
            'run_directory',
            'lammps_command',
            'mpi_command',
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