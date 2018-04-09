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

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calc_style and record_style
calc_style = 'E_vs_r_scan'
record_style = 'calculation_cohesive_energy_relation'

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
    
    # Loop over all potentials
    for pot_record in iprPy.prepare.ipotentials(dbase,
                          element=kwargs.get('potential_element', None),
                          name=kwargs.get('potential_name', None),
                          pair_style=kwargs.get('potential_pair_style', None),
                          currentIPR=iprPy.input.boolean(kwargs.get('potential_currentIPR', True))):
        potential = lmp.Potential(pot_record.content)
        pot_tar = dbase.get_tar(pot_record)
        
        # Loop over all prototypes
        for proto_record in iprPy.prepare.iprototypes(dbase,
                               natypes=kwargs.get('prototype_natypes', None),
                               name=kwargs.get('prototype_name', None),
                               spacegroup=kwargs.get('prototype_spacegroup',
                                                     None),
                               crystalfamily=kwargs.get('prototype_crystalfamily', None),
                               pearson=kwargs.get('prototype_Pearsonsymbol',
                                                  None)):
            
            # Iterate over all combinations of potentials, prototypes and symbols
            for symbols in iprPy.prepare.isymbolscombos(proto_record,
                                                        pot_record):
                
                # Create calc_key
                calc_key = str(uuid.uuid4())
                
                # Pass values to calculation 
                calc_dict = {}
                
                calc_dict['potential_file'] = pot_record.name + '.xml'
                calc_dict['potential_dir'] = pot_record.name
                calc_dict['potential_content'] = pot_record.content
                
                calc_dict['load_file'] = proto_record.name+'.xml'
                calc_dict['load_style'] = 'system_model'
                calc_dict['load_content'] = proto_record.content
                
                calc_dict['symbols'] = ' '.join(symbols)
                
                for key in singularkeys():
                    if key in kwargs:
                        calc_dict[key] = kwargs[key]
                
                # Build incomplete record
                input_dict = deepcopy(calc_dict)
                calculation.process_input(input_dict, calc_key, build=False)
                model = iprPy.buildmodel(record_style, 'calc_' + calc_style,
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
                    
                    # Add potential record file to calculation folder
                    with open(os.path.join(calc_directory, pot_record.name+'.xml'), 'w') as f:
                        f.write(pot_record.content)
                    
                    # Extract potential's tar files to calculation folder
                    pot_tar.extractall(calc_directory)
                    
                    # Add prototype record file to calculation folder
                    with open(os.path.join(calc_directory, proto_record.name+'.xml'), 'w') as f:
                        f.write(proto_record.content)

def unusedkeys():
    """
    The calculation input parameters that are not prepare input parameters.
    
    Returns
    -------
    list of str
        The list of input parameter keys ignored by prepare.
    """
    return [
            'load_options',
            'box_parameters',
            'x_axis',
            'y_axis',
            'z_axis',
            'atomshift',
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
            'lammps_command',
            'mpi_command',
            'potential_currentIPR',
            'sizemults',
            'minimum_r',
            'maximum_r',
            'number_of_steps_r',
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
            'potential_element', 
            'potential_name',
            'potential_pair_style',
            'prototype_natypes',
            'prototype_name',
            'prototype_spacegroup',
            'prototype_crystalfamily',
            'prototype_Pearsonsymbol',
           ]

if __name__ == '__main__':
    main(*sys.argv[1:])