#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
import sys
import uuid
import glob
import shutil
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

from .Bain import Bain

# Define calculation metadata
calculation_style = 'bain_transformation_map'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'
record_style = 'calculation_bain_transformation_map'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run relax_static to relax system
    results_dict = baintransformation(input_dict['lammps_command'],
                                input_dict['a_bcc'],
                                input_dict['a_fcc'],
                                input_dict['symbol'],
                                input_dict['sizemults'],
                                input_dict['potential'],
                                mpi_command = input_dict['mpi_command'],
                                num_a = input_dict['number_a_scale'],
                                num_c = input_dict['number_c_scale'],
                                min_a = input_dict['minimum_a_scale'],
                                max_a = input_dict['maximum_a_scale'],
                                min_c = input_dict['minimum_c_scale'],
                                max_c = input_dict['maximum_c_scale'],
                                etol = input_dict['energytolerance'],
                                ftol = input_dict['forcetolerance'],
                                maxiter = input_dict['maxiterations'],
                                maxeval = input_dict['maxevaluations'],
                                dmax = input_dict['maxatommotion'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)
    
def baintransformation(lammps_command, a_bcc, a_fcc, symbol, sizemults, potential,
                       mpi_command=None, num_a=23, num_c=23,
                       min_a=-0.05, max_a=1.05, min_c=-0.05, max_c=1.05,
                       etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000,
                       dmax=uc.set_in_units(0.01, 'angstrom')):
    
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Get lammps template
    template_file = 'min.template'
    template = iprPy.tools.read_calc_file(template_file, filedict)
    
    # Define constant lammps variables
    lammps_variables = {}
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%i %i %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Define bain object
    bain = Bain(a_bcc=a_bcc, a_fcc=a_fcc, symbol=symbol)
    
    energies = []
    a_scales = []
    c_scales = []
    i = 0
    # Iterate over cells
    for a_scale, c_scale, ucell in bain.itercellmap(num_a=num_a, num_c=num_c, min_a=min_a,
                                                   max_a=max_a, min_c=min_c, max_c=max_c):
    
        system = ucell.supersize(*sizemults)
    
        sim_directory = Path(str(i))
        if not sim_directory.is_dir():
            sim_directory.mkdir()
        sim_directory = sim_directory.as_posix()+'/'
            
        # Define lammps variables
        system_info = system.dump('atom_data', f=Path(sim_directory, 'atom.dat').as_posix(),
                                  potential=potential,
                                  return_pair_info=True)
        lammps_variables['atomman_system_pair_info'] = system_info
        lammps_variables['sim_directory'] = sim_directory
        
        # Write lammps input script
        lammps_script = Path(sim_directory, 'min.in')
        with open(lammps_script, 'w') as f:
            f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                             '<', '>'))
        # Run LAMMPS
        output = lmp.run(lammps_command, lammps_script.as_posix(), mpi_command,
                         logfile=Path(sim_directory, 'log.lammps').as_posix())

        # Extract output values
        thermo = output.simulations[-1]['thermo']
        E_total = uc.set_in_units(thermo.PotEng.values[-1],
                                  lammps_units['energy'])
        a_scales.append(a_scale)
        c_scales.append(c_scale)
        energies.append(E_total / system.natoms)
        
        i += 1
    
    # Return results
    results_dict = {}
    results_dict['a_scale'] = a_scales
    results_dict['c_scale'] = c_scales
    results_dict['E_coh'] = energies
    
    return results_dict

def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    # Set script's name
    input_dict['script'] = script
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['symbol'] = str(input_dict['symbol'])
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['number_a_scale'] = int(input_dict.get('number_a_scale', 23))
    input_dict['number_c_scale'] = int(input_dict.get('number_c_scale', 23))
    
    # These are calculation-specific default unitless floats
    input_dict['minimum_a_scale'] = float(input_dict.get('minimum_a_scale', -0.05))
    input_dict['maximum_a_scale'] = float(input_dict.get('maximum_a_scale', 1.05))
    input_dict['minimum_c_scale'] = float(input_dict.get('minimum_c_scale', -0.05))
    input_dict['maximum_c_scale'] = float(input_dict.get('maximum_c_scale', 1.05))

    # These are calculation-specific default floats with units
    input_dict['a_bcc'] = iprPy.input.value(input_dict, 'a_bcc',
                                    default_unit=input_dict['length_unit'])
    input_dict['a_fcc'] = iprPy.input.value(input_dict, 'a_fcc',
                                    default_unit=input_dict['length_unit'])
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.subset('lammps_minimize').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)

    # Handle sizemults
    # Convert string values to lists of numbers
    sizemults = input_dict['sizemults'].strip().split()
    for i in range(len(sizemults)):
        sizemults[i] = int(sizemults[i])
    
    # Properly divide up sizemults if 6 terms given
    if len(sizemults) == 6:
        if (sizemults[0] <= 0 
            and sizemults[0] < sizemults[1]
            and sizemults[1] >= 0
            and sizemults[2] <= 0
            and sizemults[2] < sizemults[3]
            and sizemults[3] >= 0
            and sizemults[4] <= 0
            and sizemults[4] < sizemults[5]
            and sizemults[5] >= 0):
            
            sizemults =  [[sizemults[0], sizemults[1]],
                        [sizemults[2], sizemults[3]],
                        [sizemults[4], sizemults[5]]]
        
        else:
            raise ValueError('Invalid sizemults command')
    
    # Properly divide up sizemults if 3 terms given
    elif len(sizemults) == 3:
        for i in range(3):
            
            # Add 0 before if value is positive
            if sizemults[i] > 0:
                sizemults[i] = [0, sizemults[i]]
            
            # Add 0 after if value is negative
            elif sizemults[i] < 0:
                sizemults[i] = [sizemults[i], 0]
            
            else:
                raise ValueError('Invalid sizemults command')
        
    else:
        raise ValueError('Invalid sizemults command')
    input_dict['sizemults'] = sizemults

if __name__ == '__main__':
    main(*sys.argv[1:])  