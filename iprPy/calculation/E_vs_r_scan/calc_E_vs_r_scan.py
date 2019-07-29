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
record_style = 'calculation_E_vs_r_scan'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run e_vs_r
    results_dict = e_vs_r(input_dict['lammps_command'],
                          input_dict['initialsystem'],
                          input_dict['potential'],
                          mpi_command = input_dict['mpi_command'],
                          ucell = input_dict['ucell'],
                          rmin = input_dict['minimum_r'],
                          rmax = input_dict['maximum_r'],
                          rsteps = input_dict['number_of_steps_r'])
    
    # Save data model of results
    script = Path(__file__).stem
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def e_vs_r(lammps_command, system, potential,
           mpi_command=None, ucell=None, 
           rmin=uc.set_in_units(2.0, 'angstrom'), 
           rmax=uc.set_in_units(6.0, 'angstrom'), rsteps=200):
    """
    Performs a cohesive energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    ucell : atomman.System, optional
        The fundamental unit cell correspodning to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    rmin : float, optional
        The minimum r spacing to use (default value is 2.0 angstroms).
    rmax : float, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 200).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'a_values'** (*numpy.array of float*) - All unit cell a lattice
          constants corresponding to the values explored.
        - **'Ecoh_values'** (*numpy.array of float*) - The computed cohesive
          energies for each r value.
        - **'min_cell'** (*list of atomman.System*) - Systems corresponding to
          the minima identified in the Ecoh_values.
    """
    try:
        # Get script's location if __file__ exists
        script_dir = Path(__file__).parent
    except:
        # Use cwd otherwise
        script_dir = Path.cwd()

    # Make system a deepcopy of itself (protect original from changes)
    system = deepcopy(system)
    
    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Calculate the r/a ratio for the unit cell
    r_a = r_a_ratio(ucell)
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_a = system.box.b / ucell.box.a
    lz_a = system.box.c / ucell.box.a
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
 
    # Build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    a_values = r_values / r_a
    Ecoh_values = np.empty(rsteps)
    
    # Loop over values
    for i in range(rsteps):
        
        # Rescale system's box
        a = a_values[i]
        system.box_set(a = a * lx_a, 
                       b = a * ly_a, 
                       c = a * lz_a, 
                       alpha=alpha, beta=beta, gamma=gamma, scale=True)
        
        # Get lammps units
        lammps_units = lmp.style.unit(potential.units)
        
        # Define lammps variables
        lammps_variables = {}
        system_info = system.dump('atom_data', f='atom.dat',
                                  units=potential.units,
                                  atom_style=potential.atom_style)
        lammps_variables['atomman_system_info'] = system_info
        lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
        
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
            Ecoh_values[i] = np.nan
        else:
            thermo = output.simulations[0]['thermo']
            
            if output.lammps_date < datetime.date(2016, 8, 1):
                Ecoh_values[i] = uc.set_in_units(thermo.peatom.values[-1],
                                                lammps_units['energy'])
            else:
                Ecoh_values[i] = uc.set_in_units(thermo.v_peatom.values[-1],
                                                lammps_units['energy'])
        
        # Rename log.lammps
        try:
            shutil.move('log.lammps', 'run0-'+str(i)+'-log.lammps')
        except:
            pass

    if len(Ecoh_values[np.isfinite(Ecoh_values)]) == 0:
        raise ValueError('All LAMMPS runs failed. Potential likely invalid or incompatible.')  
    
    # Find unit cell systems at the energy minimums
    min_cells = []
    for i in range(1, rsteps - 1):
        if (Ecoh_values[i] < Ecoh_values[i-1]
            and Ecoh_values[i] < Ecoh_values[i+1]):
            a = a_values[i]
            cell = deepcopy(ucell)
            cell.box_set(a = a,
                         b = a * ucell.box.b / ucell.box.a,
                         c = a * ucell.box.c / ucell.box.a, 
                         alpha=alpha, beta=beta, gamma=gamma, scale=True)
            min_cells.append(cell)
    
    # Collect results
    results_dict = {}
    results_dict['r_values'] = r_values
    results_dict['a_values'] = a_values
    results_dict['Ecoh_values'] = Ecoh_values
    results_dict['min_cell'] = min_cells
    
    return results_dict
    
def r_a_ratio(ucell):
    """
    Calculates the r/a ratio by identifying the shortest interatomic spacing, r,
    for a unit cell.
    
    Parameters
    ----------
    ucell : atomman.System
        The unit cell system to evaluate.
        
    Returns
    -------
    float
        The shortest interatomic spacing, r, divided by the unit cell's a
        lattice parameter.
    """
    r_a = ucell.box.a
    for i in range(ucell.natoms):
        for j in range(i):
            dmag = np.linalg.norm(ucell.dvect(i,j))
            if dmag < r_a:
                r_a = dmag
    return r_a / ucell.box.a

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
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['number_of_steps_r'] = int(input_dict.get('number_of_steps_r',
                                                         200))
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    input_dict['minimum_r'] = iprPy.input.value(input_dict, 'minimum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='2.0 angstrom')
    input_dict['maximum_r'] = iprPy.input.value(input_dict, 'maximum_r',
                                      default_unit=input_dict['length_unit'],
                                      default_term='6.0 angstrom')
    
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