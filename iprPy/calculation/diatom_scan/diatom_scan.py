# Python script created by Lucas Hale

# Standard Python libraries
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj


def diatom_scan(lammps_command: Union[str, LAMMPSobj],
                potential: lammpspotential,
                symbols: list,
                mpi_command: Optional[str] = None,
                rmin: unitfloat = '0.02 angstrom',
                rmax: unitfloat = '6.0 angstrom',
                rsteps: int = 300,
                usefiles: bool = False) -> dict:
    """
    Performs a diatom energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the two atoms in the diatom.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float or str, optional
        The minimum r spacing to use (default value is 0.02 angstroms).
    rmax : float or str, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 300).
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'energy_values'** (*numpy.array of float*) - The computed potential
          energies for each r value.
    """

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # File generation settings
    if usefiles:
        logfile = 'log.lammps'
        script = 'diatom.in'
    elif lmp.islib:
        logfile = 'none'
        script = None
    else:
        logfile = 'none'
        script = 'diatom.in'

    # Convert values given with units if needed
    rmin = uc.set_in_units(rmin)
    rmax = uc.set_in_units(rmax)

    # Define atype based on symbols
    symbols = am.tools.aslist(symbols)
    if len(symbols) == 1:
        atype = [1, 1]
    elif len(symbols) == 2:
        if symbols[0] != symbols[1]:
            atype = [1, 2]
        else:
            atype = [1, 1]
            symbols = symbols[:1]
    else:
        raise ValueError('symbols must have one or two values')
    
    # Initialize system
    box = am.Box.cubic(a = rmax + 1)
    system = am.System(box=box, pbc=(False, False, False), symbols=symbols)
    lmp.new_system_no_atoms(system, potential)

    # Create the two atoms. Will shift atom 2 later
    lmp.commands_string('# Create atoms')
    lmp.cmd.create_atoms(atype[0], 'single', 0.1, 0.1, 0.1, 'units', 'box')
    lmp.cmd.create_atoms(atype[1], 'single', 0.1, 0.1, 0.1, 'units', 'box')

    # Add charges if required
    if potential.atom_style == 'charge':
        charges = potential.charges(symbols)
        lmp.cmd.set('atom', 1, 'charge', charges[atype[0]-1])
        lmp.cmd.set('atom', 2, 'charge', charges[atype[1]-1])

    # Define LAMMPS variables for the rij search range
    lmp.commands_string('\n# Define LAMMPS variables for the rij search range')
    lmp.cmd.variable('rmin', 'equal', uc.get_in_units(rmin, lmp.unitsdict['length']))
    lmp.cmd.variable('rmax', 'equal', uc.get_in_units(rmax, lmp.unitsdict['length']))
    lmp.cmd.variable('rsteps', 'equal', rsteps)
    lmp.cmd.variable('delta', 'equal', '(${rmax}-${rmin})/(${rsteps}-1)')
    lmp.cmd.variable('rij', 'equal', '${rmin}+(v_i-1)*${delta}')
    lmp.cmd.variable('xpos', 'equal', '0.1+v_rij')

    # Set up thermo style
    lmp.commands_string('\n# Set up thermo style')
    lmp.cmd.thermo_style('custom', 'step', 'pe', 'v_rij')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Define integrator to keep LAMMPS from complaining
    lmp.cmd.fix('nve', 'all', 'nve')

    # Loop over r steps and evaluate
    thermos = []
    for i in lmp.loop('i', rsteps, usefiles=usefiles):

        # Update atom 2's x coordinate
        lmp.commands_string("\n# Update atom 2's x coordinate and evaluate")
        lmp.cmd.set('atom', 2, 'x', '${xpos}')
        lmp.cmd.run(0)

        # Extract thermo data
        if lmp.islib and not usefiles:
            thermos.append(lmp.last_thermo())
            lmp.cmd.reset_timestep(i)

    # Run EXE versions, get log output
    log = lmp.end_and_get_log(script)

    # Compile thermo data
    if lmp.islib and not usefiles:
        thermo = pd.DataFrame(thermos)
    else:
        thermo = log.flatten('all').thermo

    # Convert units on thermo terms
    lmp.set_thermo_units(thermo)
    thermo.v_rij = uc.set_in_units(thermo.v_rij, lmp.unitsdict['length'])

    # Collect results
    results_dict = {}
    results_dict['r_values'] = thermo.v_rij
    results_dict['energy_values'] = thermo.PotEng
    
    return results_dict
