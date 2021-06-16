#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
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
calc_style = 'dislocation_Peierls_Nabarro_stress'
record_style = 'calculation_dislocation_Peierls_Nabarro_stress'

def main(*args):
    """Main function called when script is executed directly."""
    
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
    """
    High-throughput prepare function for the calculation.
    
    Parameters
    ----------
    dbase : iprPy.Database
        The database to access and create new records for.
    run_directory : str
        The path to the local directory where the prepared calculation
        instances will be placed.
    **kwargs
        Arbitrary keyword arguments.
    """
    
    # Initialize Calculation instance
    calculation = iprPy.Calculation(calc_style)
    
    # Build record_df
    record_df = dbase.get_records_df(style=record_style, full=False, flat=True)
    
    # Build defect model record dictionary and df (single dbase access)
    defect_record_dict = {}
    defect_record_df = []
    for defect_record in dbase.iget_records(style='dislocation_monopole'):
        defect_record_dict[defect_record.name] = defect_record
        defect_record_df.append(defect_record.todict())
    defect_record_df = pd.DataFrame(defect_record_df)
    
    # Limit by defect name
    if 'dislocation_name' in kwargs:
        defect_names = iprPy.tools.aslist(kwargs['dislocation_name'])
        defect_selection = defect_record_df.id.isin(defect_names)
        defect_record_df = defect_record_df[defect_selection]
    
    # Get parent records
    if 'parent_records' in kwargs:
        parent_records = kwargs['parent_records']
    else:
        parent_records = iprPy.prepare.icalculations(dbase,
                            record_style = 'calculation_dislocation_Peierls_Nabarro',
                            symbol = kwargs.get('symbol_name', None),
                            family = kwargs.get('family_name', None),
                            potential = kwargs.get('potential_name', None))
    
    load_record_dict = {}
    gamma_record_dict = {}
    
    # Loop over parent records
    for parent_record in parent_records:
        parent_dict = parent_record.todict()
        
        # Get load_record from dbase only once per file
        load_record_key = os.path.splitext(parent_dict['load_file'])[0]
        if load_record_key in load_record_dict:
            load_record = load_record_dict[load_record_key]
        else:
            load_record = dbase.get_record(name=load_record_key)
            load_record_dict[load_record_key] = load_record
        
        # Get gamma_record from dbase only once per file
        gamma_record_key = parent_dict['gammasurface_calc_key']
        if gamma_record_key in gamma_record_dict:
            gamma_record = gamma_record_dict[gamma_record_key]
        else:
            gamma_record = dbase.get_record(name=gamma_record_key)
            gamma_record_dict[gamma_record_key] = gamma_record
        
        # Loop over defect model records with family name matching parent record
        matches = defect_record_df['family'] == parent_dict['family']
        defect_keys = defect_record_df[matches].id.tolist()
        for defect_key in defect_keys:
            defect_record = defect_record_dict[defect_key]
            
            # Create calc_key
            calc_key = str(uuid.uuid4())
            
            # Define values for calc_*.in file
            calc_dict = {}
            
            calc_dict['load_file'] = load_record.name+'.xml'
            calc_dict['load_style'] = 'system_model'
            calc_dict['load_content'] = load_record.content
            calc_dict['load_options'] = parent_dict['load_options']
            
            calc_dict['dislocation_model'] = defect_record.name+'.xml'
            calc_dict['dislocation_content'] = defect_record.content
            
            calc_dict['gammasurface_model'] = gamma_record.name+'.xml'
            calc_dict['gammasurface_content'] = gamma_record.content
            
            calc_dict['peierlsnabarro_model'] = parent_record.name+'.xml'
            calc_dict['peierlsnabarro_content'] = parent_record.content
            
            for key in singularkeys():
                if key in kwargs:
                    calc_dict[key] = kwargs[key]
            
            # Build incomplete record
            input_dict = {}
            for key in calc_dict:
                if calc_dict[key] != '':
                    input_dict[key] = deepcopy(calc_dict[key])
            calculation.process_input(input_dict, calc_key, build=False)
            model = iprPy.buildmodel(record_style,
                                     'calc_' + calc_style,
                                     input_dict)
            
            new_record = iprPy.Record(name=calc_key,
                                      content=model.xml(),
                                      style=record_style)
            
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
                
                # Add load record file to calculation folder
                with open(os.path.join(calc_directory,load_record.name+'.xml'), 'w') as f:
                    f.write(load_record.content)
                
                # Add gamma record file to calculation folder
                with open(os.path.join(calc_directory, gamma_record.name+'.xml'), 'w') as f:
                    f.write(gamma_record.content)
                
                # Add parent record file to calculation folder
                with open(os.path.join(calc_directory, parent_record.name+'.xml'), 'w') as f:
                    f.write(parent_record.content)
                
                # Add defect record file to calculation folder
                with open(os.path.join(calc_directory, defect_record.name+'.xml'), 'w') as f:
                    f.write(defect_record.content)

def unusedkeys():
    """
    The calculation input parameters that are not prepare input parameters.
    
    Returns
    -------
    list of str
        The list of input parameter keys ignored by prepare.
    """
    return [
            'load_file',
            'load_style',
            'load_options',
            'symbols',
            'box_parameters',
            'dislocation_model',
            'gammasurface_model',
            'peierlsnabarro_model',
           ]

def singularkeys():
    """
    The prepare input parameters that can be assigned only one value.
    
    Returns
    -------
    list of str
        The list of input parameter keys that are limited to singular values.
    """
    return [
            'database',
            'run_directory',
            'delta_tau_xy',
            'delta_tau_yy',
            'delta_tau_yz',
            'minimize_style',
            'minimize_options',
            'tausteps',
            'fullstress',
            'cdiffstress',
            'length_unit',
            'pressure_unit',
            'energy_unit',
            'force_unit',
           ]

def multikeys():
    """
    The prepare input parameters that can be assigned multiple values.
    
    Returns
    -------
    list of str
        The list of input parameter keys that can have multiple values.
    """
    return [
            'potential_name',
            'symbol_name',
            'family_name',
            'dislocation_name',
           ]

if __name__ == '__main__':
    main(*sys.argv[1:])