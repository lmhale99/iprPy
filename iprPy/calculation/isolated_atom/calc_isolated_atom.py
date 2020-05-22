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
calculation_style = 'isolated_atom'
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
    
    # Run diatom
    results_dict = isolated_atom(input_dict['lammps_command'],
                                 input_dict['potential'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def isolated_atom(lammps_command, potential, mpi_command=None):
    """
    Evaluates the isolated atom energy for each elemental model of a potential.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'energy'** (*dict*) - The computed potential energies for each
          symbol.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}
 
    # Initialize dictionary
    energydict = {}
    
    # Initialize single atom system 
    box = am.Box.cubic(a=1)
    atoms = am.Atoms(atype=1, pos=[[0.5, 0.5, 0.5]])
    system = am.System(atoms=atoms, box=box, pbc=[False, False, False])

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Define lammps variables
    lammps_variables = {}

    # Loop over symbols
    for symbol in potential.symbols:
        system.symbols = symbol

        # Add charges if required
        if potential.atom_style == 'charge':
            system.atoms.prop_atype('charge', potential.charges(system.symbols))

        # Save configuration
        system_info = system.dump('atom_data', f='isolated.dat',
                                  potential=potential,
                                  return_pair_info=True)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        # Write lammps input script
        template_file = 'run0.template'
        lammps_script = 'run0.in'
        template = iprPy.tools.read_calc_file(template_file, filedict)
        with open(lammps_script, 'w') as f:
            f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                             '<', '>'))
        
        # Run lammps and extract data
        output = lmp.run(lammps_command, lammps_script, mpi_command)
        energy = output.simulations[0]['thermo'].PotEng.values[-1]
        energydict[symbol] = uc.set_in_units(energy, lammps_units['energy'])
    
    # Collect results
    results_dict = {}
    results_dict['energy'] = energydict
    
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
    # None for this calculation
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)

if __name__ == '__main__':
    main(*sys.argv[1:])