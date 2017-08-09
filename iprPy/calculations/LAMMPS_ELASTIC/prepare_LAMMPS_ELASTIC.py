#!/usr/bin/env python

# Standard library imports
from __future__ import division, absolute_import, print_function
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
calc_style = 'LAMMPS_ELASTIC'
record_style = 'calculation_system_relax'

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

    # Build potential dictionaries (single dbase access)
    pot_record_dict = {}
    pot_tar_dict = {}
    for pot_record in dbase.iget_records(style='potential_LAMMPS'):
        pot_record_dict[pot_record.name] = pot_record
    
    # Get parent records
    if 'parent_records' in kwargs:
        parent_records = kwargs['parent_records']
    else:
        parent_records = iprPy.prepare.icalculations(dbase,
                            record_style = 'calculation_cohesive_energy_relation',
                            symbol = kwargs.get('symbol_name', None),
                            family = kwargs.get('family_name', None),
                            potential = kwargs.get('potential_name', None))
    
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
        
        # Loop over number_min_states
        for i in xrange(parent_dict['number_min_states']):
            if i == 0:
                load_options = 'key minimum-atomic-system'
            else:
                load_options = 'key minimum-atomic-system index '+str(i)
            
            # Loop over strainrange values
            strainranges = kwargs.get('strainrange', '')
            for strainrange in iprPy.tools.iaslist(strainranges):
                
                # Create calc_key
                calc_key = str(uuid.uuid4())
                
                # Define values for calc_*.in file
                calc_dict = {}
                
                calc_dict['potential_file'] = pot_record.name + '.xml'
                calc_dict['potential_dir'] = pot_record.name
                calc_dict['potential_content'] = pot_record.content
                
                calc_dict['load_file'] = parent_record.name+'.xml'
                calc_dict['load_style'] = 'system_model'
                calc_dict['load_content'] = parent_record.content
                calc_dict['load_options'] = load_options

                calc_dict['strainrange'] = strainrange
                
                for key in singularkeys():
                    if key in kwargs:
                        calc_dict[key] = kwargs[key]
                
                # Build incomplete record
                input_dict = deepcopy(calc_dict)
                calculation.process_input(input_dict, calc_key, build=False)
                model = iprPy.buildmodel(record_style,
                                         'calc_' + calc_style,
                                         input_dict)
                new_record = iprPy.Record(name=calc_key,
                                          content=model.xml(),
                                          style=record_style)
                
                #Check if record is new
                if new_record.isnew(record_df=record_df):
                
                    # Assign '' to any unassigned keys
                    for key in unusedkeys()+singularkeys()+multikeys():
                        if key not in calc_dict:
                            calc_dict[key] = ''
                            
                    #Add record to database
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
    
def unusedkeys():
    """
    The calculation input parameters that are not prepare input parameters.
    
    Returns
    -------
    list of str
        The list of input parameter keys ignored by prepare.
    """
    return [
            'symbols',
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
            'sizemults',
            'convergevalues',
            'energytolerance',
            'forcetolerance',
            'maxiterations',
            'maxevaluations',
            'maxatommotion',
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
            'strainrange',
           ]
            
if __name__ == '__main__':
    main(*sys.argv[1:])