# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
import random
from typing import Optional, Union

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate, aslist

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# iprPy imports
from ...tools import read_calc_file

def free_energy(lammps_command: str,
                system: am.System,
                potential: lmp.Potential,
                temperature: float,
                mpi_command: Optional[str] = None,
                spring_constants: Union[float, npt.ArrayLike, None] = None,
                equilsteps: int = 25000,
                switchsteps: int = 50000,
                springsteps: int = 50000,
                pressure: float = 0.0,
                randomseed: Optional[int] = None) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
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
  
    if spring_constants is None:
        spring_constants = einstein_spring_constants(lammps_command, system,
                                                     potential, temperature,
                                                     mpi_command=mpi_command,
                                                     equilsteps=equilsteps,
                                                     springsteps=springsteps,
                                                     randomseed=randomseed)
    else:
        spring_constants = np.asarray(aslist(spring_constants))
        assert len(spring_constants) == system.natypes, 'number of spring constants must match number of atypes'

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    timestep = lmp.style.timestep(potential.units)
    
    if randomseed is None:
        randomseed = random.randint(1, 900000000)

    # Define lammps variables
    lammps_variables = {}
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Build spring fixes for each atype
    spring_fix = '# Define spring fixes\n'
    spring_hamil = 'v_pe'

    for i in range(system.natypes):
        spring_fix += f'group atype_{i+1} type {i+1}\n'
        spring_fix += f'fix ti_spring_{i+1} atype_{i+1} ti/spring {spring_constants[i]} {switchsteps} {equilsteps} function 2\n'
        spring_hamil += f'-f_ti_spring_{i+1}'

    # Other run settings
    lammps_variables['timestep'] = timestep
    lammps_variables['switchsteps'] = switchsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['spring_fix'] = spring_fix
    lammps_variables['spring_hamil'] = spring_hamil
    lammps_variables['temperature'] = temperature
    lammps_variables['temperature_damp'] = 100 * timestep
    lammps_variables['randomseed'] = randomseed
    
    # Write lammps input script
    lammps_script = 'free_energy.in'
    template = read_calc_file('iprPy.calculation.free_energy',
                              'free_energy.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps 
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
    
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

def einstein_spring_constants(lammps_command: str,
                              system: am.System,
                              potential: lmp.Potential,
                              temperature: float,
                              mpi_command: Optional[str] = None,
                              equilsteps: int = 1000,
                              springsteps: int = 50000,
                              randomseed: Optional[int] = None) -> dict:
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
    runsteps : int, optional
        The number of integration steps to perform (default is 50000).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_initial'** (*str*) - The name of the initial dump file
          created.
        - **'symbols_initial'** (*list*) - The symbols associated with the
          initial dump file.
        - **'dumpfile_final'** (*str*) - The name of the final dump file
          created.
        - **'symbols_final'** (*list*) - The symbols associated with the final
          dump file.
        - **'nsamples'** (*int*) - The number of thermodynamic samples included
          in the mean and standard deviation estimates.  Can also be used to
          estimate standard error values assuming that the thermo step size is
          large enough (typically >= 100) to assume the samples to be
          independent.
        - **'E_pot'** (*float*) - The mean measured potential energy.
        - **'measured_pxx'** (*float*) - The measured x tensile pressure of the
          relaxed system.
        - **'measured_pyy'** (*float*) - The measured y tensile pressure of the
          relaxed system.
        - **'measured_pzz'** (*float*) - The measured z tensile pressure of the
          relaxed system.
        - **'measured_pxy'** (*float*) - The measured xy shear pressure of the
          relaxed system.
        - **'measured_pxz'** (*float*) - The measured xz shear pressure of the
          relaxed system.
        - **'measured_pyz'** (*float*) - The measured yz shear pressure of the
          relaxed system.
        - **'temp'** (*float*) - The mean measured temperature.
        - **'E_pot_std'** (*float*) - The standard deviation in the measured
          potential energy values.
        - **'measured_pxx_std'** (*float*) - The standard deviation in the
          measured x tensile pressure of the relaxed system.
        - **'measured_pyy_std'** (*float*) - The standard deviation in the
          measured y tensile pressure of the relaxed system.
        - **'measured_pzz_std'** (*float*) - The standard deviation in the
          measured z tensile pressure of the relaxed system.
        - **'measured_pxy_std'** (*float*) - The standard deviation in the
          measured xy shear pressure of the relaxed system.
        - **'measured_pxz_std'** (*float*) - The standard deviation in the
          measured xz shear pressure of the relaxed system.
        - **'measured_pyz_std'** (*float*) - The standard deviation in the
          measured yz shear pressure of the relaxed system.
        - **'temp_std'** (*float*) - The standard deviation in the measured
          temperature values.
    """
  
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    timestep = lmp.style.timestep(potential.units)
    
    if randomseed is None:
        randomseed = random.randint(1, 900000000)

    # Define lammps variables
    lammps_variables = {}
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Build msd computes and outputs based on natypes
    msd_compute = '# Define computes for msd for each atom type\n'
    msd_average = '# Start cumulative averaging of msd\n'
    msd_thermo = ''
    for i in range(system.natypes):
        msd_compute += f'group group{i+1} type {i+1}\n'
        msd_compute += f'compute msd{i+1} group{i+1} msd com yes\n'
        msd_compute += f'variable msd{i+1} equal c_msd{i+1}[4]\n'
        msd_average += f'fix msd{i+1} all ave/time 1 100 100 v_msd{i+1} ave running\n'
        msd_thermo += f'f_msd{i+1} '

    # Other run settings
    lammps_variables['runsteps'] = springsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['timestep'] = timestep
    lammps_variables['msd_compute'] = msd_compute
    lammps_variables['msd_average'] = msd_average
    lammps_variables['msd_thermo'] = msd_thermo
    lammps_variables['temperature'] = temperature
    lammps_variables['temperature_damp'] = 100 * timestep
    lammps_variables['randomseed'] = randomseed
    
    # Write lammps input script
    lammps_script = 'msd.in'
    template = read_calc_file('iprPy.calculation.free_energy',
                              'msd.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, logfile='log.msd.lammps')
    
    # Extract LAMMPS thermo data. 
    thermo = output.simulations[1].thermo

    spring_constant = []
    for i in range(system.natypes):
        msd = thermo[f'f_msd{i+1}'].values[-1]
        k = (3 * uc.unit['kB'] * temperature) / msd
        spring_constant.append(k)
    
    return spring_constant

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