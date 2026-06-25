# Python script created by Lucas Hale

# Standard Python libraries
from typing import Optional, Union

import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
from atomman.typing import lammpspotential
from atomman.lammps import LAMMPS, LAMMPSobj

def isolated_atom(lammps_command: Union[str, LAMMPSobj],
                  potential: lammpspotential,
                  mpi_command: Optional[str] = None,
                  usefiles: bool = False) -> dict:
    """
    Evaluates the isolated atom energy for each elemental model of a potential.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'energy'** (*dict*) - The computed potential energies for each
          symbol.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # File generation settings
    if usefiles:
        logfile = 'log.lammps'
        script = 'run0.in'
    else:
        logfile = 'none'
        script = None
        
    # Initialize dictionary
    energydict = {}
    
    lmp.commands_string('\n# Initialize empty system and potential')
    box = am.Box.cubic(a=1)
    system = am.System(box=box, pbc=(False, False, False), symbols=potential.symbols)
    lmp.new_system_no_atoms(system, potential, logfile=logfile)

    lmp.commands_string('\n# Set up thermo style')
    lmp.cmd.thermo_style('custom', 'step', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    lmp.commands_string('\n# Define integrator to keep LAMMPS from complaining')
    lmp.cmd.fix('nve', 'all', 'nve')

    # Loop over symbols
    thermos = []
    for i, symbol in enumerate(potential.symbols):

        # Create atom on first loop
        if i == 0:
            lmp.commands_string('\n# Create atom')
            lmp.cmd.create_atoms(1, 'single', 0.5, 0.5, 0.5, 'units', 'box')
        
        # Change atom type on later loops
        else:
            lmp.commands_string('\n# Change atom type')
            lmp.cmd.set('atom', 1, 'type', i+1)

        # Set charge if needed  
        if potential.atom_style == 'charge':
            lmp.cmd.set('atom', 1, 'charge', potential.charges(symbol)[0])

        lmp.commands_string('\n# Perform a run 0 to evaluate the system')
        lmp.cmd.run(0)

        # Extract thermo data
        if lmp.islib and not usefiles:
            thermos.append(lmp.last_thermo())
            lmp.cmd.reset_timestep(i)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    # Compile thermo data
    if lmp.islib and not usefiles:
        thermo = pd.DataFrame(thermos)
    else:
        thermo = log.flatten('all').thermo

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)
        
    # Pull energy values out for each symbol
    energydict = {}
    for i, symbol in enumerate(potential.symbols):
        energydict[symbol] = thermo['PotEng'].values[i]
    
    # Collect results
    results_dict = {}
    results_dict['energy'] = energydict
    
    return results_dict