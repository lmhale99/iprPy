# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union
from pathlib import Path
import random

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def melting_temperature(lammps_command: Union[str, LAMMPSobj],
                        system: am.System,
                        potential: lammpspotential,
                        temperature_guess: float,
                        mpi_command: Optional[str] = None,
                        pressure: unitfloat = 0.0,
                        temperature_solid: Optional[float] = None,
                        temperature_liquid: Optional[float] = None,
                        ptm_structures: Optional[str] = None,
                        meltsteps: int = 10000,
                        scalesteps: int = 10000,
                        runsteps: int = 200000,
                        thermosteps: int = 100,
                        dumpsteps: Optional[int] = None,
                        randomseed1: Optional[int] = None,
                        randomseed2: Optional[int] = None,
                        usefiles: bool = False) -> dict:
    """
    Creates a solid-liquid phase coexistence simulation to estimate the melting
    temperature.  The boundary for the two phases will be perpendicular to the
    z-axis and positioned halfway along the c box vector.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The initial system to perform the calculation on.  This should be a
        supercell with dimensions along the z direction roughly twice the
        dimensions in the other directions.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    temperature_guess : float, optional
        The initial guess for the melting temperature. The closer to the actual
        temperature the faster and more likely convergence will be possible.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    pressure : float or str, optional
        The target pressure to use with the barostat.  Default value is 0.0.
    temperature_liquid : float or None, optional
        The initial temperature to use for the liquid region to melt the crystal.
        Default value of None will use 1.25 * temperature_guess.
    temperature_solid : float or None, optional
        The initial temperature to use for the solid region.
        Default value of None will use 0.5 * temperature_guess.
    meltsteps : int, optional
        The number of integration steps to perform with half of the system
        at temperature_solid and half of the system at temperature_liquid to
        create the two phase configuration.  Default value is 10000.
    scalesteps : int, optional
        The number of integration steps after meltsteps where the temperature
        of the atoms in the two phases are both scaled to temperature_guess.
        This ensures that the full system starts near temperature_guess for the
        main runsteps.  Default value is 10000.
    runsteps : int, optional
        The number of nph integration steps to perform on the two-phase system
        to hopefully get a stable coexistence at the melting temperature.
    thermosteps : int, optional
        Thermo values will be reported every this many steps. Default is
        100.
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps. Default is None,
        which sets dumpsteps equal to meltsteps + scalesteps + runsteps.
    randomseed1 : int or None, optional
        Random number seed used by LAMMPS in creating velocities for the liquid
        region.  Default is None which will select random ints between 1 and
        900000000.
    randomseed2 : int or None, optional
        Random number seed used by LAMMPS in creating velocities for the solid
        region.  Default is None which will select random ints between 1 and
        900000000.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'temp'** (*float*) - The mean measured temperature.
    """
    logfile = 'log.lammps'
    if usefiles:
        script = 'liquid.in'
    else:
        script = None

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pressure = uc.set_in_units(pressure)
    
    # Handle default values
    randomseed1 = am.lammps.seed(randomseed1)
    randomseed2 = am.lammps.seed(randomseed2)
    if dumpsteps is None:
        dumpsteps = meltsteps + scalesteps + runsteps
    if temperature_liquid is None:
        temperature_liquid = 1.25 * temperature_guess
    if temperature_solid is None:
        temperature_solid = 0.5 * temperature_guess
    
    # Boundary position between the two phases
    zboundary = system.box.origin[2] + 0.5 * system.box.cvect[2]

    # Simulation dump file keys
    dump_keys = ['id', 'type', 'x', 'y', 'z', 'c_pe', 'c_ke']

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep
    pressure_damp = 1000 * timestep

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    # Split system into top and bot regions
    lmp.cmd.region('top', 'block', 'INF', 'INF', 'INF', 'INF', zboundary, 'INF')
    lmp.cmd.region('bot', 'block', 'INF', 'INF', 'INF', 'INF', 'INF', zboundary)
    lmp.cmd.group('top', 'region', 'top')
    lmp.cmd.group('bot', 'region', 'bot')

    # Per-atom property computes
    lmp.cmd.compute('pe', 'all', 'pe/atom')
    lmp.cmd.compute('ke', 'all', 'ke/atom')

    # Add polyhedral template matching
    if ptm_structures is not None:
        lmp.cmd.compute('ptm', 'all', 'ptm/atom', ptm_structures, 0.15)
        dump_keys.append('c_ptm[1]')

    # Thermo output definition
    lmp.cmd.thermo(thermosteps)
    lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                         'lx', 'ly', 'lz', 'pxx', 'pyy', 'pzz')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    lmp.cmd.timestep(timestep)

    # Define dump files
    lmp.cmd.dump('dumpit', 'all', 'custom', dumpsteps, '*.dump', *dump_keys)
    lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')

    # Create velocities
    lmp.cmd.velocity('top', 'create', temperature_liquid, randomseed1)
    lmp.cmd.velocity('bot', 'create', temperature_solid, randomseed2)

    # Set barostat to use throughout
    lmp.cmd.fix('nph', 'all', 'nph', 'aniso', pressure, pressure, pressure_damp)

    # Set different thermostats to top and bottom to create two phases
    lmp.cmd.fix('beren_liquid', 'top', 'temp/berendsen',
                temperature_liquid, temperature_liquid, temperature_damp)
    lmp.cmd.fix('beren_solid', 'bot', 'temp/berendsen',
                temperature_solid, temperature_solid, temperature_damp)
    lmp.cmd.run(meltsteps)

    # Update thermostats to scale to the guess temperature
    lmp.cmd.unfix('beren_liquid')
    lmp.cmd.unfix('beren_solid')
    lmp.cmd.fix('beren_liquid', 'top', 'temp/berendsen',
                temperature_liquid, temperature_guess, temperature_damp)
    lmp.cmd.fix('beren_solid', 'bot', 'temp/berendsen',
                temperature_solid, temperature_guess, temperature_damp)
    lmp.cmd.run(scalesteps)

    # Remove thermostats and relax
    lmp.cmd.unfix('beren_liquid')
    lmp.cmd.unfix('beren_solid')
    lmp.cmd.run(runsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
   
    thermo = log.simulations[2].thermo
    
    results_dict = {}
    results_dict['melting_temperature'] = thermo.Temp[round(len(thermo)/2):].mean()

    results_dict['fraction_solids'] = []
    if ptm_structures is not None:
        first_to_read = meltsteps + scalesteps + runsteps / 2
        for i in range(dumpsteps, meltsteps + scalesteps + runsteps+1, dumpsteps):
            if i < first_to_read:
                continue
            dump = am.load('atom_dump', f'{i}.dump')
            num_solid = np.sum(dump.atoms.view['c_ptm[1]'] != 0)
            results_dict['fraction_solids'].append(num_solid / dump.natoms)

    return results_dict