# Python script created by Peter Winstel and Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

from scipy.integrate import trapezoid
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj


def diffusion_liquid(lammps_command: Union[str, LAMMPSobj],
                     system: am.System,
                     potential: lammpspotential,
                     temperature: float,
                     mpi_command: Optional[str] = None,
                     timestep: Optional[unitfloat] = None,
                     equilsteps: int = 0,
                     runsteps: int = 2000,
                     simruns: int = 100,
                     msd_start: int = 500,
                     createvelocities: bool = False,
                     randomseed: Optional[int] = None,
                     usefiles: bool = False) -> dict:
    """
    Calculates the diffusion constant for a liquid system using both
    mean squared displacements and the velocity auto-correlation function.

    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        the LAMMPS implemented potential to use.
    temperature : float
        The temperature to run at.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel. If not given, LAMMPS
        will run serially.
    timestep : float, str or None, optional
        The amount of time to increase each frame of the simulation. The 
        default value is given by the default value for the specified LAMMPS
        unit system.
    equilsteps : int, optional
        How many timesteps to run to equilibrate the system before starting the
        diffusion calculations. Default value is 0.
    runsteps : int, optional
        How many timesteps each short diffusion simulation will run for.  This
        should be a good value for the velocity auto correlation function,
        typically in the low 1000's.  Default value is 2000.
    simruns : int, optional
        The number of short diffusion simulations to run. The VACF and short
        MSD values are averaged over the runs.  Default value of 100.
    msd_start : int, optional
        The starting timestep for including MSD data in the MSD diffusion
        calculations.  Initial values should be ignored due to correlation
        with the initial atomic positions for the MSD run.  Default value is
        500.
    createvelocities : bool, optional
        If True, velocities will be created for the atoms prior to running the
        simulations.  Default value is False, which assumes the initial system
        already has velocity information.  Typically, if this is True then
        equilsteps > 0.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:

        -**'diffusion_msd_short'** (*float*) - The diffusion constant estimate
        obtained using the slope of the mean squared displacement averaged over
        all separate simulations.
        -**'diffusion_msd_long'** (*float*) - The diffusion constant estimate
        obtained from the mean squared displacement slope of the full combined
        simulation run.
        -**'diffusion_vacf'** (*float*) - The diffusion constant estimate
        obtained using the velocity auto correlation function averaged over
        all separate simulations.
        -**'measured_temperature'** (*float*) - The mean observed temperature
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'liquid.in'
    else:
        script = None

    # Check/select a randomseed value
    randomseed = am.lammps.seed(randomseed)

    # Set timestep in atomman and LAMMPS units
    if timestep is None:
        timestep_lammps = am.lammps.style.timestep(lmp.potential.units)
        timestep = uc.set_in_units(timestep_lammps, lmp.unitsdict['time'])
    else:
        timestep = uc.set_in_units(timestep)
        timestep_lammps = uc.get_in_units(timestep, lmp.unitsdict['time'])
    temperature_damp = 100 * timestep_lammps

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('\n# Integrator definition')
    lmp.cmd.timestep(timestep_lammps)
    lmp.cmd.fix('NVT', 'all', 'nvt', 'temp', temperature, temperature, temperature_damp)

    if createvelocities:
        lmp.commands_string('\n# Create new velocities')
        lmp.cmd.velocity('all', 'create', temperature, randomseed, 'mom',
                        'yes', 'rot', 'yes', 'dist', 'gaussian')

    lmp.commands_string('\n# Equilibration run')
    lmp.cmd.run(equilsteps)
    lmp.cmd.reset_timestep(0)

    lmp.commands_string('\n# MSD long calculation parameters')
    lmp.cmd.compute('msdLong', 'all', 'msd', 'com', 'yes')

    lmp.commands_string('\n# Simulation loops')
    for i in lmp.loop('i', simruns):

        lmp.commands_string('\n# MSD short calculation parameters')
        lmp.cmd.compute('msdShort', 'all', 'msd', 'com', 'yes')
        
        lmp.commands_string('\n# VACF calculation parameters')
        lmp.cmd.compute('vacf', 'all', 'vacf')

        lmp.commands_string('\n# Set thermo outputs')
        thermo_keys = ['step', 'temp',
                       'c_vacf[1]', 'c_vacf[2]', 'c_vacf[3]', 'c_vacf[4]',
                       'c_msdShort[1]', 'c_msdShort[2]', 'c_msdShort[3]', 'c_msdShort[4]',
                       'c_msdLong[1]', 'c_msdLong[2]', 'c_msdLong[3]', 'c_msdLong[4]']
        lmp.cmd.thermo_style('custom', *thermo_keys)
        lmp.cmd.thermo_modify('format', 'float', '%.17e')
        lmp.cmd.thermo(1)

        lmp.commands_string('\n# Run')
        lmp.cmd.run(runsteps)

        lmp.commands_string('\n# Clear short computes')
        lmp.cmd.uncompute('msdShort')
        lmp.cmd.uncompute('vacf')


    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    # Define complex LAMMPS output units
    msd_unit = f"{lmp.unitsdict['length']}^2"
    vacf_unit = f"{lmp.unitsdict['velocity']}^2"

    # Extract time from first simulation
    time_short = log.simulations[1].thermo.Step.values * timestep

    # Loop over simulations and extract results
    msd_short = np.empty((simruns, time_short.shape[0]))
    vacf = np.empty((simruns, time_short.shape[0]))
    for i, sim in enumerate(log.simulations[1:]):
        thermo = sim.thermo
        msd_short[i,:] = uc.set_in_units(thermo['c_msdShort[4]'], msd_unit)
        vacf[i,:] = uc.set_in_units(thermo['c_vacf[4]'], vacf_unit)

    # Combine simulations for the long estimate
    allsim = log.flatten(firstindex=1)
    thermo = allsim.thermo
    time_long = thermo.Step * timestep
    msd_long = uc.get_in_units(thermo['c_msdLong[4]'], msd_unit)


    # Compute diffusion constant estimates
    def line(x, slope, intercept):
        return intercept + x * slope
    
    slope = curve_fit(line, time_short[msd_start:], msd_short.mean(axis=0)[msd_start:])[0][0]
    diffusion_msd_short = slope / 6

    slope = curve_fit(line, time_long[msd_start:], msd_long[msd_start:])[0][0]
    diffusion_msd_long = slope / 6

    diffusion_vacf = trapezoid(vacf.mean(axis=0), time_short) / 3

    msd_short_plot(time_short, msd_short, msd_start)
    msd_long_plot(time_long, msd_long, msd_start)
    vacf_plot(time_short, vacf)


    # Build results dict
    results = {}
    results['diffusion_msd_short'] = diffusion_msd_short
    results['diffusion_msd_long'] = diffusion_msd_long
    results['diffusion_vacf'] = diffusion_vacf
    results['measured_temperature'] = allsim.thermo.Temp.mean()

    results['lammps_output'] = log

    return results


def msd_short_plot(time_short, msd_short, msd_start):
    """
    Create a plot of MSD vs t for the short simulations
    """
    t = uc.get_in_units(time_short, 'ps')
    msd = uc.get_in_units(msd_short, 'angstrom^2')

    plt.plot(t[msd_start:], msd.T[msd_start:])
    plt.plot(t[msd_start:], msd.mean(axis=0)[msd_start:], 'k-', linewidth=3)
    plt.xlim(t[msd_start], t[-1])
    plt.ylim(0.0, None)

    plt.title('MSD Short')
    plt.xlabel('time (ps)')
    plt.ylabel('MSD (angstrom^2)')
    plt.savefig('MSD short')
    plt.close()

def vacf_plot(time_short, vacf):
    """
    Create a plot of VACF vs t for the short simulations
    """
    t = uc.get_in_units(time_short, 'ps')
    v = uc.get_in_units(vacf, 'angstrom/ps')

    plt.plot(t, v.T)
    plt.plot(t, v.mean(axis=0), 'k-', linewidth=3)
    plt.xlim(0, t[-1])

    plt.title('VACF')
    plt.xlabel('time (ps)')
    plt.ylabel('VACF (angstrom/ps)')
    plt.savefig('VACF')
    plt.close()

def msd_long_plot(time_long, msd_long, msd_start):
    """
    Create a plot of MSD vs t for the full simulation
    """
    t = uc.get_in_units(time_long, 'ps')
    msd = uc.get_in_units(msd_long, 'angstrom^2')

    plt.plot(t[msd_start:], msd[msd_start:], 'k-', linewidth=3)
    plt.xlim(t[msd_start], t[-1])
    plt.ylim(0.0, None)

    plt.title('MSD Long')
    plt.xlabel('time (ps)')
    plt.ylabel('MSD (angstrom^2)')
    plt.savefig('MSD Long')
    plt.close()