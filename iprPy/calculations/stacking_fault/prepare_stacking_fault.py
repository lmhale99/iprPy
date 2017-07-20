#!/usr/bin/env python

# Standard library imports
from __future__ import print_function, division
import os
import sys
import glob
import uuid
import shutil
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# http://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calc_style and record_style
calc_style = 'stacking_fault'
record_style = 'calculation-stacking-fault'

def main(*args):
    """main function called when script is executed directly"""
    
    # Read input script
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, singularkeys=singularkeys())

    # Open database
    dbase = iprPy.database_fromdict(input_dict)
    
    # Pull out run_directory
    run_directory = input_dict.pop('run_directory')
    
    # Call prepare
    prepare(dbase, run_directory, **input_dict)
    
def prepare(dbase, run_directory, **kwargs):
    """high-throughput prepare function for the calculation"""
    
    # Initialize Calculation instance
    calculation = iprPy.Calculation(calc_style)
    
    # Build record_df
    record_df = build_record_df(dbase, record_style)
    
    # Build potential dictionaries (single dbase access)
    pot_record_dict = {}
    pot_tar_dict = {}
    for pot_record in dbase.iget_records(style='potential-LAMMPS'):
        pot_record_dict[pot_record.name] = pot_record
        
    # Build defect model record dictionary and df (single dbase access)
    defect_record_dict = {}
    defect_record_df = []
    for defect_record in dbase.iget_records(style='stacking-fault'):
        defect_record_dict[defect_record.name] = defect_record
        defect_record_df.append(defect_record.todict())
    defect_record_df = pd.DataFrame(defect_record_df)
    
    # Limit by defect name
    if 'stackingfault_name' in kwargs:
        defect_names = iprPy.tools.aslist(kwargs['stackingfault_name'])
        defect_selection = defect_record_df.id.isin(defect_names)
        defect_record_df = defect_record_df[defect_selection]
    
    # Get parent records
    if 'parent_records' in kwargs:
        parent_records = kwargs['parent_records']
    else:
        parent_records = iprPy.prepare.icalculations(dbase, 
                                                     record_style = 'calculation-system-relax',
                                                     symbol =       kwargs.get('symbol_name', None), 
                                                     family =       kwargs.get('family_name', None),
                                                     potential =    kwargs.get('potential_name', None))
    # Loop over parent records
    for parent_record in parent_records:
        parent_dict = parent_record.todict()
    
        # Load potential
        pot_record = pot_record_dict[parent_dict['potential_LAMMPS_id']]
        potential = lmp.Potential(pot_record.content)
        
        # Get pot_tar from dbase only once per potential
        if parent_dict['potential_LAMMPS_id'] in pot_tar_dict:
            pot_tar = pot_tar_dict[parent_dict['potential_LAMMPS_id']]
        else:
            pot_tar = dbase.get_tar(pot_record)
            pot_tar_dict[parent_dict['potential_LAMMPS_id']] = pot_tar
        
        # Loop over shiftfraction values
        shifts1 = kwargs.get('stackingfault_shiftfraction1', '')
        shifts2 = kwargs.get('stackingfault_shiftfraction2', '')
        
        for shift1 in iprPy.tools.iaslist(shifts1):
            for shift2 in iprPy.tools.iaslist(shifts2):
        
                # Loop over defect model records with family name matching parent record
                matches = defect_record_df['family'] == parent_dict['family']
                defect_keys = defect_record_df[matches].id.tolist()
                for defect_key in defect_keys:
                    defect_record = defect_record_dict[defect_key]
                    
                    # Create calc_key
                    calc_key = str(uuid.uuid4())
                    
                    # Define values for calc_*.in file
                    calc_dict = {}
            
                    calc_dict['potential_file'] =       pot_record.name + '.xml'
                    calc_dict['potential_dir'] =        pot_record.name
                    calc_dict['potential_content'] =    pot_record.content
                    
                    calc_dict['load_file'] =            parent_record.name+'.xml'
                    calc_dict['load_style'] =           'system_model'
                    calc_dict['load_content'] =         parent_record.content
                    calc_dict['load_options'] =         'key relaxed-atomic-system'

                    calc_dict['stackingfault_shiftfraction1'] =   shift1
                    calc_dict['stackingfault_shiftfraction2'] =   shift2
                    calc_dict['stackingfault_model'] =    defect_record.name+'.xml'
                    calc_dict['stackingfault_content'] =  defect_record.content
                    
                    for key in singularkeys():
                        if key in kwargs:
                            calc_dict[key] = kwargs[key]

                    # Build incomplete record
                    input_dict = deepcopy(calc_dict)
                    calculation.process_input(input_dict, calc_key, build=False)
                    model = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict)
                    new_record = iprPy.Record(name=calc_key, content=model.xml(), style=record_style)
                    
                    # Check if record is new
                    if new_record.isnew(record_df=record_df):
                    
                        # Assign '' to any unassigned keys
                        for key in unusedkeys()+singularkeys()+multikeys():
                            if key not in calc_dict:
                                calc_dict[key] = ''
                    
                        # Add record to database
                        dbase.add_record(record=new_record)
                        
                        # Generate calculation folder    
                        calc_directory = os.path.join(run_directory, calc_key)
                        os.makedirs(calc_directory)
                        
                        # Save inputfile to calculation folder
                        inputfile = iprPy.tools.filltemplate(calculation.template, calc_dict, '<', '>')
                        with open(os.path.join(calc_directory, 'calc_' + calc_style + '.in'), 'w') as f:
                            f.write(inputfile)

                        # Add calculation files to calculation folder
                        for calc_file in calculation.files:
                            shutil.copy(calc_file, calc_directory)
                        
                        # Add potential record file to calculation folder
                        with open(os.path.join(calc_directory, pot_record.name+'.xml'), 'w') as f:
                            f.write(pot_record.content)
                            
                        # Extract potential's tar files to calculation folder
                        pot_tar.extractall(calc_directory)
                        
                        # Add parent record file to calculation folder
                        with open(os.path.join(calc_directory, parent_record.name+'.xml'), 'w') as f:
                            f.write(parent_record.content)
                            
                        # Add defect record file to calculation folder
                        with open(os.path.join(calc_directory, defect_record.name+'.xml'), 'w') as f:
                            f.write(defect_record.content)
                    
def build_record_df(dbase, record_style):
    """Constructs a pandas.DataFrame for all records in a database of a given record_type"""
    df = []
    for record in dbase.iget_records(style=record_style):
        df.append(record.todict(full=False, flat=True))
    return pd.DataFrame(df)

def unusedkeys():
    """List the calc_*.in key terms that are ignored by the prepare function."""
    return ['symbols',
            'box_parameters',
            'x_axis',
            'y_axis',
            'z_axis',
            'atomshift',
            'stackingfault_cutboxvector',
            'stackingfault_faultpos',
            'stackingfault_shiftvector1', 
            'stackingfault_shiftvector2'
            ]    
                    
def singularkeys():
    """List the prepare_*.in key terms that are restricted to having only one value."""
    return ['database',
            'run_directory',
            'lammps_command',
            'mpi_command',
            'sizemults',
            'energytolerance',
            'forcetolerance',
            'maxiterations',
            'maxevaluations',
            'maxatommotion',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit']

def multikeys():
    """List the prepare_*.in key terms that can have multiple values."""
    return ['potential_name',
            'symbol_name',
            'family_name',
            'stackingfault_name',
            'stackingfault_shiftfraction1',
            'stackingfault_shiftfraction2']
            
if __name__ == '__main__':
    main(*sys.argv[1:])         