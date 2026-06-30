# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj
from atomman.tools import aslist

def free_energy(lammps_command: Union[str, LAMMPSobj],
                system: am.System,
                potential: lammpspotential,
                temperature: float,
                mpi_command: Optional[str] = None,
                spring_constants: Union[float, npt.ArrayLike, None] = None,
                equilsteps: int = 25000,
                switchsteps: int = 50000,
                springsteps: int = 50000,
                pressure: unitfloat = 0.0,
                createvelocities: bool = True,
                randomseed: Optional[int] = None,
                usefiles: bool = False) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to run at.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    spring_constants : float, array-like object or None, optional
        The Einstein solid spring constants to assign to each atom type.  If
        None (default), then a separate simulation will estimate them using
        mean squared displacements.
    equilsteps : int, optional
        The number of equilibration timesteps at the beginning of simulations
        to ignore before evaluations.  This is used at the beginning of both
        the spring constant estimate and before each thermo switch run.
        Default value is 25000.
    switchsteps : int, optional
        The number of integration steps to perform during each of the two
        switch runs.  Default value is 50000.
    springsteps : int, optional
        The number of integration steps to perform for the spring constants
        estimation, which is only done if spring_constants is None.  Default
        value is 50000.
    pressure : float, optional
        A value of pressure to use for computing the Gibbs free energy from
        the Helmholtz free energy.  NOTE: this is not used to equilibrate the
        system during this calculation!  Default value is 0.0.
    randomseed : int or None, optional
        Random number seed used by LAMMPS.  Default is None which will select
        a random int between 1 and 900000000.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'spring_constants'** (*list*) - The Einstein spring constants
          assigned to each atom type.
        - **'work_forward'** (*float*) - The work/atom during the
          forward switching step.
        - **'work_reverse'** (*float*) - The work/atom during the
          reverse switching step.
        - **'work'** (*float*) - The reversible work/atom.
        - **'Helmholtz_reference'** (*float*) - The Helmholtz free energy/atom
          for the reference Einstein solid.
        - **'Helmholtz'** (*float*) - The Helmholtz free energy/atom.
        - **'Gibbs'** (*float*) - The Gibbs free energy/atom.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pressure = uc.set_in_units(pressure)

    # Set randomseed
    randomseed = am.lammps.seed(randomseed)
    
    if spring_constants is None:
        # Run spring constants simulation
        spring_constants = einstein_spring_constants(lmp, system,
                                                     temperature,
                                                     equilsteps,
                                                     springsteps,
                                                     createvelocities,
                                                     randomseed,
                                                     usefiles)
    else:
        # Check given spring constant values
        spring_constants = aslist(spring_constants)
        if len(spring_constants) != system.natypes:
            raise ValueError('number of spring constants must match number of atypes')

    # Run thermodynamic integration simulation
    thermodynamic_integration(lmp, system, temperature, spring_constants,
                              equilsteps, switchsteps, createvelocities,
                              randomseed, usefiles)
    
    # Extract LAMMPS thermo data for the switching runs.
    hamil_forward = np.loadtxt('forward_switch.txt', skiprows=1)
    hamil_reverse = np.loadtxt('reverse_switch.txt', skiprows=1)

    # Integrate the Hamiltonians to compute the switching work
    work_forward, work_reverse, work = integrate_for_work(hamil_forward,
                                                          hamil_reverse)

    # Get values per atype for computing the Einstein solid free energy reference
    natoms = []
    for i in range(system.natypes):
        natoms.append(np.sum(system.atoms.atype == i+1))
    masses = potential.masses(system.symbols)
    volume = system.box.volume

    # Evaluate the reference free energy
    F_ein = einstein_free_energy(temperature, volume, spring_constants, masses, natoms)

    # Compute the Helmholtz free energy of the system
    F_sys = F_ein + work

    # Compute the Gibbs free energy of the system
    G_sys = F_sys + pressure * volume

    results = {}
    results['spring_constants'] = spring_constants
    results['work_forward'] = work_forward / system.natoms
    results['work_reverse'] = work_reverse / system.natoms
    results['work'] = work / system.natoms
    results['Helmholtz_reference'] = F_ein / system.natoms
    results['Helmholtz'] = F_sys / system.natoms
    results['Gibbs'] = G_sys / system.natoms
    
    return results

def einstein_spring_constants(lmp: LAMMPSobj,
                              system: am.System,
                              temperature: float,
                              equilsteps: int,
                              springsteps: int,
                              createvelocities: bool,
                              randomseed: int,
                              usefiles: bool) -> list:
    """
    Runs an nvt simulation to evaluate atomic mean squared displacements in
    order to estimate a spring constant for an Einstein model.
    
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
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    springsteps : int, optional
        The number of integration steps to perform (default is 50000).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    
    Returns
    -------
    spring_constant : list
        The estimated Einstein spring constants
    """
    logfile = 'log_msd.lammps'
    if usefiles:
        script = 'msd.in'
    else:
        script = None

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('# Define computes for msd for each atom type')
    for i in range(system.natypes):
        lmp.cmd.group(f'group{i+1}', 'type', i+1)
        lmp.cmd.compute(f'msd{i+1}', f'group{i+1}', 'msd', 'com', 'yes')
        lmp.cmd.variable(f'msd{i+1}', 'equal', f'c_msd{i+1}[4]')

    lmp.commands_string('\n# Thermo settings for equilibrium run')
    lmp.cmd.thermo(100)
    lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                         'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    lmp.cmd.timestep(timestep)

    if createvelocities:
        lmp.commands_string('\n# Create velocities')
        lmp.cmd.velocity('all', 'create', temperature, randomseed,
                         'mom', 'yes', 'rot', 'yes', 'dist', 'gaussian')

    lmp.commands_string('\n# Define thermostat')
    lmp.cmd.fix('nvt', 'all', 'nvt', 'temp',
                temperature, temperature, temperature_damp)

    lmp.commands_string('\n# Equilibration run')
    lmp.cmd.run(equilsteps)

    lmp.commands_string('# Start cumulative averaging of msd')
    msd_thermo = []
    for i in range(system.natypes):
        lmp.cmd.fix(f'msd{i+1}', 'all', 'ave/time', 1, 100, 100,
                    f'v_msd{i+1}', 'ave', 'running')
        msd_thermo.append(f'f_msd{i+1}')

    lmp.commands_string('\n# Thermo settings for spring estimate run')
    lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                         'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', *msd_thermo)
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    lmp.commands_string('\n# Spring constant estimate run')
    lmp.cmd.run(springsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    # Extract LAMMPS thermo data. 
    thermo = log.simulations[1].thermo

    spring_constant = []
    for i in range(system.natypes):
        msd = thermo[f'f_msd{i+1}'].values[-1]
        k = (3 * uc.unit['kB'] * temperature) / msd
        spring_constant.append(k)
    
    return spring_constant

def thermodynamic_integration(lmp: LAMMPSobj,
                              system: am.System,
                              temperature: float,
                              spring_constants: list,
                              equilsteps: int,
                              switchsteps: int,
                              createvelocities: bool,
                              randomseed: int,
                              usefiles: bool):
    logfile = 'log_ti.lammps'
    if usefiles:
        script = 'free_energy.in'
    else:
        script = None
    
    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.cmd.timestep(timestep)
    lmp.cmd.variable('pe', 'equal', 'pe')

    if createvelocities:
        lmp.commands_string('\n# Create velocities')
        lmp.cmd.velocity('all', 'create', temperature, randomseed,
                         'mom', 'yes', 'rot', 'yes', 'dist', 'gaussian')

    lmp.commands_string('\n# Define thermostat')
    lmp.cmd.fix('nve', 'all', 'nve')

    lmp.commands_string('\n# Define spring fixes')
    for i in range(system.natypes):
        lmp.cmd.group(f'atype_{i+1}', 'type', f'{i+1}')
        lmp.cmd.fix(f'ti_spring_{i+1}', f'atype_{i+1}', 'ti/spring', spring_constants[i], switchsteps, equilsteps, 'function', 2)

    lmp.commands_string('\n# Langevin thermostat must be placed after ti/spring fixes')
    lmp.cmd.fix('langevin', 'all', 'langevin',
                temperature, temperature, temperature_damp, randomseed, 'zero', 'yes')
    lmp.cmd.compute('temp_com', 'all', 'temp/com')
    lmp.cmd.fix_modify('langevin', 'temp', 'temp_com')

    lmp.commands_string('\n# Compute the Hamiltonian as potential energy minus the ti/spring energies')
    spring_hamil = 'v_pe'
    for i in range(system.natypes):
        spring_hamil += f'-f_ti_spring_{i+1}'
    lmp.cmd.variable('hamil', 'equal', spring_hamil)

    lmp.commands_string('\n# Define minimal thermo')
    lmp.cmd.thermo(0)
    lmp.cmd.thermo_style('custom', 'step', 'c_temp_com', 'pe')

    lmp.commands_string('\n# Equilibrate and forward switch')
    lmp.cmd.run(equilsteps)
    lmp.cmd.fix('forward_switch', 'all', 'print', 1, '"${hamil}"',
                'screen', 'no', 'file', 'forward_switch.txt')
    lmp.cmd.run(switchsteps)
    lmp.cmd.unfix('forward_switch')

    lmp.commands_string('\n# Equilibrate and reverse switch')
    lmp.cmd.run(equilsteps)
    lmp.cmd.fix('reverse_switch', 'all', 'print', 1, '"${hamil}"',
                'screen', 'no', 'file', 'reverse_switch.txt')
    lmp.cmd.run(switchsteps)
    lmp.cmd.unfix('reverse_switch')

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

def einstein_free_energy(temperature: float,
                         volume: float,
                         spring_constants: npt.ArrayLike,
                         masses: npt.ArrayLike,
                         natoms: npt.ArrayLike):
    """
    Computes the free energy for the Einstein solid at a given temperature.

    Parameters
    ----------
    temperature : float
        The temperature to use.
    volume : float
        The volume of the system.
    spring_constants : array-like object
        The Einstein solid spring constants for each atom type.
    masses : array-like object
        The atomic masses for each atom type.
    natoms : array-like object
        The number of atoms for each atom type.

    Returns
    -------
    float
        The total free energy evaluated for the Einstein solid.
    """
    # Get constants
    kB = uc.unit['kB']
    ħ = uc.unit['ħ']
    π = np.pi
    
    # Remap inputs for the equations
    T = temperature
    V = volume
    k = np.asarray(aslist(spring_constants))
    m = np.asarray(aslist(masses))
    N = np.asarray(aslist(natoms))
    assert len(k) == len(m), 'Same number of spring constants and masses are required'
    assert len(k) == len(N), 'Same number of spring constants and natoms are required'
    
    # Compute omega
    ω = np.sqrt(k / m)
    
    # Compute the Einstein free energy
    F_einstein = np.sum(3 * N * kB * T * np.log((ħ * ω) / (kB * T)))
    
    # Compute the center of mass correction
    F_com_corr = np.sum(kB * T * np.log((N / V) * ((2 * π * kB * T) / (N * k))**(3/2)))

    return F_einstein + F_com_corr

def integrate_for_work(hamil_forward, hamil_reverse):

    def Δλ(τ1, τ2):
        """Compute the change in λ between τ values"""
        return 70*(τ2**9-τ1**9) - 315*(τ2**8-τ1**8) + 540*(τ2**7-τ1**7) - 420*(τ2**6-τ1**6) + 126*(τ2**5-τ1**5)

    # Numerically compute the forward and reverse work using the trapezoidal rule and Δλ
    τ = np.linspace(0.0, 1.0, len(hamil_forward))
    work_forward = np.sum((hamil_forward[1:] + hamil_forward[:-1]) /2 * Δλ(τ[:-1], τ[1:]))
    
    τ = np.linspace(1.0, 0.0, len(hamil_reverse))
    work_reverse = np.sum((hamil_reverse[1:] + hamil_reverse[:-1]) /2 * Δλ(τ[:-1], τ[1:]))
    
    # Average difference for reversible work
    work = (work_forward - work_reverse) / 2

    return work_forward, work_reverse, work