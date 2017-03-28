#!/usr/bin/env python

#Standard library imports
import os
import sys
import uuid
import shutil

#http://www.numpy.org/
import numpy as np

#http://pandas.pydata.org/
import pandas as pd

#https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_style__ = 'bcc_grain_boundary'
__record_style__ = 'calculation-grain-boundary-search'

def main(*args):
    calculation = iprPy.Calculation(__calc_style__)
    
    with open(args[0]) as f:
        prepare_dict = read_input(f)
        
    #open database
    dbase = iprPy.database_fromdict(prepare_dict)
    
    #Build record_df
    record_df = build_record_df(dbase, __record_style__)
    
    #Load relax_structure records
    for parent_record in iprPy.prepare.icalculations(dbase, 
                                                     record_style = 'calculation-structure-relax',
                                                     symbol =       prepare_dict['symbol_name'], 
                                                     prototype =    'A2--W--bcc',
                                                     potential =    prepare_dict['potential_name']):
        parent_dict = parent_record.todict()
        
        #Skip if strainrange not 1e-6 and calc_script not relax_structure
        if not np.isclose(parent_dict['strainrange'], 1e-6): continue
        if parent_dict['calc_script'] != 'calc_refine_structure': continue
        
        #Load potential, symbols, alat, and cohesive energy
        pot_record = dbase.get_record(name=parent_dict['potential_id'], style='LAMMPS-potential')
        potential = lmp.Potential(pot_record.content)
        pot_tar = dbase.get_tar(pot_record)
        symbols = parent_dict['symbols']
        E_coh = parent_dict['E_cohesive']
        alat = parent_dict['final_a']
        
        #Loop over grain boundaries
        for x_axis_1, y_axis_1, z_axis_1, x_axis_2, y_axis_2, z_axis_2 in zip(prepare_dict['x_axis_1'], 
                                                                              prepare_dict['y_axis_1'], 
                                                                              prepare_dict['z_axis_1'], 
                                                                              prepare_dict['x_axis_2'], 
                                                                              prepare_dict['y_axis_2'], 
                                                                              prepare_dict['z_axis_2']):
            
            #Create calc_key
            calc_key = str(uuid.uuid4())
            
            #Define values for calc_*.in file
            calc_dict = {}
            calc_dict['lammps_command'] =   prepare_dict['lammps_command']
            calc_dict['mpi_command'] =      prepare_dict['mpi_command']
            calc_dict['potential_file'] =   pot_record.name + '.xml'
            calc_dict['potential_dir'] =    pot_record.name
            calc_dict['symbols'] =          symbols * 3
            calc_dict['alat'] =             alat
            calc_dict['E_coh'] =            E_coh
            calc_dict['x_axis_1'] =         x_axis_1
            calc_dict['y_axis_1'] =         y_axis_1
            calc_dict['z_axis_1'] =         z_axis_1
            calc_dict['x_axis_2'] =         x_axis_2
            calc_dict['y_axis_2'] =         y_axis_2
            calc_dict['z_axis_2'] =         z_axis_2
            calc_dict['x_stepsize'] =       prepare_dict['x_stepsize']
            calc_dict['z_stepsize'] =       prepare_dict['z_stepsize']
            calc_dict['length_unit'] =      prepare_dict['length_unit']
            calc_dict['pressure_unit'] =    prepare_dict['pressure_unit']
            calc_dict['energy_unit'] =      prepare_dict['energy_unit']
            calc_dict['force_unit'] =       prepare_dict['force_unit']

            #Build inputfile by filling in calculation's template
            inputfile = iprPy.tools.filltemplate(calculation.template, calc_dict, '<', '>')
            
            #Read inputfile to build input_dict
            input_dict = calculation.read_input(inputfile, calc_key)
            
            #Define additional input_dict terms
            input_dict['potential'] = potential
            input_dict['load_file'] = parent_record.content
            iprPy.input.system_family(input_dict)
            
            #Build incomplete record
            new_record = iprPy.Record(name=calc_key, content=calculation.data_model(input_dict).xml(), style=__record_style__)
            
            #Check if record is new
            if is_new(record_df, new_record):
            
                #Add record to database
                dbase.add_record(record=new_record)
                
                #Generate calculation folder    
                calc_directory = os.path.join(prepare_dict['run_directory'], calc_key)
                os.makedirs(calc_directory)
                
                #Save inputfile to calculation folder
                with open(os.path.join(calc_directory, 'calc_' + __calc_style__ + '.in'), 'w') as f:
                    f.write(inputfile)

                #Add calculation files to calculation folder
                for calc_file in calculation.files:
                    shutil.copy(calc_file, calc_directory)  
                
                #Add potential record file to calculation folder
                with open(os.path.join(calc_directory, pot_record.name+'.xml'), 'w') as f:
                    f.write(pot_record.content)
                    
                #Extract potential's tar files to calculation folder    
                pot_tar.extractall(calc_directory)
                
                #Add parent record file to calculation folder
                with open(os.path.join(calc_directory, parent_record.name+'.xml'), 'w') as f:
                    f.write(parent_record.content)    

def build_record_df(dbase, record_style):
    """Constructs a pandas.DataFrame for all records in a database of a given record_type"""
    df = []
    for record in dbase.iget_records(style=record_style):
        df.append(record.todict(full=False))
    return pd.DataFrame(df)
    
def is_new(record_df, record):
    """Checks if a matching calculation record already exists"""
    
    if len(record_df) == 0:
        return True
    
    record_dict = record.todict(full=False)

    #compare simple terms
    test_df = record_df[(record_df['calc_script'] ==         record_dict['calc_script']) &
                        (record_df['load'] ==                record_dict['load']) &
                        (record_df['load_options'] ==        record_dict['load_options']) &
                        (np.isclose(record_df['temperature'],record_dict['temperature'])) &
                        (np.isclose(record_df['pressure_xx'],record_dict['pressure_xx'])) &
                        (np.isclose(record_df['pressure_yy'],record_dict['pressure_yy'])) &
                        (np.isclose(record_df['pressure_zz'],record_dict['pressure_zz'])) ]

    #Compare complex terms
    test = np.empty(len(test_df), dtype=bool)
    for i in xrange(len(test_df)):
        
        test[i] = (np.all(test_df.iloc[i].sizemults == record_dict['sizemults']))

    test_df = test_df[test]
   
    if len(test_df) > 0:
        return False
    else:
        return True  

def read_input(f):
    """Read the given input file, assign default values and check lengths of multiple terms"""
    
    prepare_dict = iprPy.tools.parseinput(f, singularkeys=singularkeys())
    
    #Assign default values
    prepare_dict['mpi_command'] =    prepare_dict.get('mpi_command', '')
    
    prepare_dict['potential_name'] = prepare_dict.get('potential_name', None)
    
    prepare_dict['length_unit'] =    prepare_dict.get('length_unit',   '')
    prepare_dict['pressure_unit'] =  prepare_dict.get('pressure_unit', '')
    prepare_dict['energy_unit'] =    prepare_dict.get('energy_unit',   '')
    prepare_dict['force_unit'] =     prepare_dict.get('force_unit',    '')

    #Check multiple terms
    prepare_dict['x_axis_1'] = iprPy.tools.aslist(prepare_dict['x_axis_1'])
    prepare_dict['y_axis_1'] = iprPy.tools.aslist(prepare_dict['y_axis_1'])
    prepare_dict['z_axis_1'] = iprPy.tools.aslist(prepare_dict['z_axis_1'])
    prepare_dict['x_axis_2'] = iprPy.tools.aslist(prepare_dict['x_axis_2'])
    prepare_dict['y_axis_2'] = iprPy.tools.aslist(prepare_dict['y_axis_2'])
    prepare_dict['z_axis_2'] = iprPy.tools.aslist(prepare_dict['z_axis_2'])
    
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['y_axis_1'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['z_axis_1'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['x_axis_2'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['y_axis_2'])
    assert len(prepare_dict['x_axis_1']) == len(prepare_dict['z_axis_2'])
    
    return prepare_dict
    
def singularkeys():
    return ['database',
            'run_directory', 
            'lammps_command',
            'mpi_command',
            'x_stepsize',
            'z_stepsize',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit']

if __name__ == '__main__':
    main(*sys.argv[1:])              