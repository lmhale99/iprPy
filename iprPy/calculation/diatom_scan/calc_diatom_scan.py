#!/usr/bin/env python

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

# Define record_style
record_style = 'calculation_diatom_scan'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run diatom
    results_dict = diatom(input_dict['lammps_command'],
                          input_dict['potential'],
                          input_dict['symbols'],
                          mpi_command = input_dict['mpi_command'],
                          rmin = input_dict['minimum_r'],
                          rmax = input_dict['maximum_r'],
                          rsteps = input_dict['number_of_steps_r'])
    
    # Save data model of results
    script = Path(__file__).stem
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def diatom(lammps_command, potential, symbols,
           mpi_command=None, 
           rmin=uc.set_in_units(0.02, 'angstrom'), 
           rmax=uc.set_in_units(6.0, 'angstrom'), rsteps=300):
    """
    Performs a diatom energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the two atoms in the diatom.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float, optional
        The minimum r spacing to use (default value is 0.02 angstroms).
    rmax : float, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 300).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'energy_values'** (*numpy.array of float*) - The computed potential
          energies for each r value.
    """
    try:
        # Get script's location if __file__ exists
        script_dir = Path(__file__).parent
    except:
        # Use cwd otherwise
        script_dir = Path.cwd()
 
    # Build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    energy_values = np.empty(rsteps)
    
    # Define atype based on symbols
    symbols = iprPy.tools.aslist(symbols)
    if len(symbols) == 1:
        atype = [1, 1]
    elif len(symbols) == 2:
        atype = [1, 2]
    else:
        raise ValueError('symbols must have one or two values')
    
    # Initialize system (will shift second atom's position later...)
    box = am.Box.cubic(a = rmax + 1)
    atoms = am.Atoms(atype=atype, pos=[[0.1, 0.1, 0.1], [0.1, 0.1, 0.1]])
    system = am.System(atoms=atoms, box=box, pbc=[False, False, False], symbols=symbols)

    # Add charges if required
    if potential.atom_style == 'charge':
        system.atoms.prop_atype('charge', potential.charges(system.symbols))

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Define lammps variables
    lammps_variables = {}

    # Loop over values
    for i in range(rsteps):
        
        # Shift second atom's x position
        system.atoms.pos[1] = np.array([0.1 + r_values[i], 0.1, 0.1])

        # Save configuration
        system_info = system.dump('atom_data', f='diatom.dat',
                                  potential=potential,
                                  return_pair_info=True)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        # Write lammps input script
        template_file = Path(script_dir, 'run0.template')
        lammps_script = 'run0.in'
        with open(template_file) as f:
            template = f.read()
        with open(lammps_script, 'w') as f:
            f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                             '<', '>'))
        
        # Run lammps and extract data
        try:
            output = lmp.run(lammps_command, lammps_script, mpi_command)
        except:
            energy_values[i] = np.nan
        else:
            energy = output.simulations[0]['thermo'].PotEng.values[-1]
            energy_values[i] = uc.set_in_units(energy, lammps_units['energy'])

    if len(energy_values[np.isfinite(energy_values)]) == 0:
        raise ValueError('All LAMMPS runs failed. Potential likely invalid or incompatible.')
    
    # Collect results
    results_dict = {}
    results_dict['r_values'] = r_values
    results_dict['energy_values'] = energy_values
    
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
    input_dict['number_of_steps_r'] = int(input_dict.get('number_of_steps_r',
                                                         300))
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    input_dict['minimum_r'] = iprPy.input.value(input_dict, 'minimum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='0.02 angstrom')
    input_dict['maximum_r'] = iprPy.input.value(input_dict, 'maximum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='6.0 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)

if __name__ == '__main__':
    main(*sys.argv[1:])