#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from pathlib import Path
import sys
import uuid
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

# Define calculation metadata
calculation_style = 'bond_angle_scan'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Call calculation's function(s)
    results_dict = bondscan(input_dict['lammps_command'],
                            input_dict['potential'],
                            input_dict['symbols'],
                            mpi_command = input_dict['mpi_command'],
                            rmin = input_dict['minimum_r'],
                            rmax = input_dict['maximum_r'],
                            rnum = input_dict['number_of_steps_r'],
                            thetamin = input_dict['minimum_theta'],
                            thetamax = input_dict['maximum_theta'],
                            thetanum = input_dict['number_of_steps_theta'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def bondscan(lammps_command, potential, symbols, mpi_command=None,
             rmin=0.5, rmax=5.5, rnum=100,
             thetamin=1.0, thetamax=180, thetanum=100):
    """
    Performs a three-body bond angle energy scan over a range of interatomic
    spaces, r, and angles, theta.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the three atoms in the cluster.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float, optional
        The minimum value for the r_ij and r_ik spacings. Default value is 0.5.
    rmax : float, optional
        The maximum value for the r_ij and r_ik spacings. Default value is 5.5.
    rnum : int, optional
        The number of r_ij and r_ik spacings to evaluate. Default value is 100.
    thetamin : float, optional
        The minimum value for the theta angle. Default value is 1.0.
    thetamax : float, optional
        The maximum value for the theta angle. Default value is 180.0.
    thetanum : int, optional
        The number of theta angles to evaluate. Default value is 100.
        
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'cluster'** (*cluster.Cluster3Atom*) - Cluster object with all measured
          coordinates and energies.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}
 
    # Create cluster object
    cluster = am.cluster.BondAngleMap(rmin=rmin, rmax=rmax, rnum=rnum,
                           thetamin=thetamin, thetamax=thetamax, thetanum=thetanum,
                           symbols=symbols)
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    
    # Add range parameters
    lammps_variables['rmin'] = rmin
    lammps_variables['rmax'] = rmax
    lammps_variables['rnum'] = rnum
    lammps_variables['thetamin'] = thetamin
    lammps_variables['thetamax'] = thetamax
    lammps_variables['thetanum'] = thetanum

    # Add atomic types
    if len(cluster.symbols) == 1:
        natypes = 1
        atype = np.array([1,1,1])
        symbols = cluster.symbols
    elif len(cluster.symbols) == 3:
        symbols, atype = np.unique(cluster.symbols, return_inverse=True)
        atype += 1
        natypes = len(symbols) 
    lammps_variables['natypes'] = natypes
    lammps_variables['atype1'] = atype[0]
    lammps_variables['atype2'] = atype[1]
    lammps_variables['atype3'] = atype[2]
    
    # Add potential information
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['atom_style'] = potential.atom_style
    lammps_variables['units'] = potential.units

    # Build lammps input script
    # Read template file
    template_file = 'bondscan.template'
    script_file = 'bondscan.in'
    template = iprPy.tools.read_calc_file(template_file, filedict)
    with open(script_file, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps and extract data
    lmp.run(lammps_command, script_file, mpi_command=mpi_command, logfile=None, screen=False)
    energies = uc.set_in_units(np.loadtxt('energies.txt'), lammps_units['energy'])
    
    # Round energies to a specified precision
    str_energies = []
    for energy in energies:
        str_energies.append(np.format_float_scientific(energy, precision=5))
    cluster.df.energy = np.array(str_energies, dtype=float)
    
    # Collect results
    results_dict = {}
    results_dict['cluster'] = cluster
    
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
    input_dict['symbols'] = input_dict['symbols'].split()
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['number_of_steps_r'] = int(input_dict.get('number_of_steps_r', 100))
    input_dict['number_of_steps_theta'] = int(input_dict.get('number_of_steps_theta', 100))
    
    # These are calculation-specific default unitless floats
    input_dict['minimum_theta'] = float(input_dict.get('minimum_theta', 1.0))
    input_dict['maximum_theta'] = float(input_dict.get('maximum_theta', 180.0))
    
    # These are calculation-specific default floats with units
    input_dict['minimum_r'] = iprPy.input.value(input_dict, 'minimum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='0.5 angstrom')
    input_dict['maximum_r'] = iprPy.input.value(input_dict, 'maximum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='5.5 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)

if __name__ == '__main__':
    main(*sys.argv[1:])