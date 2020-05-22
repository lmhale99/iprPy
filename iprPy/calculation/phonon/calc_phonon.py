#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from pathlib import Path
import sys
import uuid
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://matplotlib.org/
import matplotlib.pyplot as plt

# https://atztogo.github.io/phonopy/phonopy-module.html
import phonopy

# https://atztogo.github.io/spglib/python-spglib.html
import spglib

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calculation metadata
calculation_style = 'phonon'
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
    
    # Run phonon
    results_dict = phonon(input_dict['lammps_command'],
                          input_dict['ucell'],
                          input_dict['potential'],
                          mpi_command = input_dict['mpi_command'],
                          a_mult = input_dict['sizemults'][0][1] - input_dict['sizemults'][0][0],
                          b_mult = input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0],
                          c_mult = input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0],
                          distance = input_dict['displacementdistance'],
                          symprec = input_dict['symmetryprecision'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def phonon(lammps_command, ucell, potential, mpi_command=None, a_mult=3, b_mult=3, c_mult=3,
           distance=0.01, symprec=1e-5):
    
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

    # Generate pair_info
    pair_info = potential.pair_info(ucell.symbols)
    
    # Use spglib to find primitive unit cell of ucell
    convcell = ucell.dump('spglib_cell')
    primcell = spglib.find_primitive(convcell, symprec=symprec)
    primucell = am.load('spglib_cell', primcell, symbols=ucell.symbols).normalize()
    
    # Initialize Phonopy object
    phonon = phonopy.Phonopy(primucell.dump('phonopy_Atoms'), [[a_mult, 0, 0], [0, b_mult, 0], [0, 0, c_mult]])
    phonon.generate_displacements(distance=distance)
    
    # Loop over displaced supercells to compute forces
    forcearrays = []
    for supercell in phonon.supercells_with_displacements:
        
        # Save to LAMMPS data file
        system = am.load('phonopy_Atoms', supercell)
        system_info = system.dump('atom_data', f='disp.dat')
        
        # Define lammps variables
        lammps_variables = {}
        lammps_variables['atomman_system_info'] = system_info
        lammps_variables['atomman_pair_info'] = pair_info

        # Set dump_modify_format based on lammps_date
        if lammps_date < datetime.date(2016, 8, 3):
            lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e"'
        else:
            lammps_variables['dump_modify_format'] = 'float %.13e'

        # Write lammps input script
        template_file = 'phonon.template'
        lammps_script = 'phonon.in'
        template = iprPy.tools.read_calc_file(template_file, filedict)
        with open(lammps_script, 'w') as f:
            f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
        
        # Run LAMMPS
        lmp.run(lammps_command, 'phonon.in', mpi_command=mpi_command)
        
        # Extract forces from dump file
        results = am.load('atom_dump', 'forces.dump')
        forces = uc.set_in_units(results.atoms.force, lammps_units['force'])
        forcearrays.append(forces)
    
    # Set computed forces
    phonon.set_forces(forcearrays)
    
    # Save to yaml file    
    phonon.save('phonopy_params.yaml')
    
    # Compute band structure    
    phonon.produce_force_constants()
    phonon.auto_band_structure(plot=True)
    
    plt.savefig(Path('.', 'band.png'), dpi=400)
    plt.close()
    
    # Compute total density of states
    phonon.auto_total_dos(plot=True)
    plt.savefig('total_dos.png', dpi=400)
    plt.close()
    
    # Compute partial density of states
    phonon.auto_projected_dos(plot=True)
    plt.savefig('projected_dos.png', dpi=400)
    plt.close()
    
    # Compute thermal properties
    phonon.run_thermal_properties()
    phonon.plot_thermal_properties()
    plt.savefig('thermal.png', dpi=400)
    plt.close()
    
    return {}

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
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    input_dict['symmetryprecision'] = float(input_dict.get('symmetryprecision', 1e-5))
    
    # These are calculation-specific default floats with units
    input_dict['displacementdistance'] = iprPy.input.value(input_dict, 'displacementdistance',
                                                default_unit=input_dict['length_unit'],
                                                default_term='0.01 angstrom')

    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)

    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)
        
if __name__ == '__main__':
    main(*sys.argv[1:])