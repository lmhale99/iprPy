# Python script created by Peter Winstel and Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://matplotlib.org/
import matplotlib.pyplot as plt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def viscosity_green_kubo(lammps_command: Union[str, LAMMPSobj],
                         system: am.System,
                         potential: lammpspotential,
                         temperature: float,
                         mpi_command: Optional[str] = None,
                         timestep: Optional[unitfloat] = None,
                         runsteps: int = 1000000,
                         equilsteps: int = 0,
                         createvelocities: bool = False,
                         randomseed: Optional[int] = None,
                         usefiles: bool = False) -> dict:
    """
    Calculates the viscosity for a liquid system using the Green-Kubo
    method.

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
    timestep : float, optional
        The amount of time to increase each frame of the simulation. The 
        default value is given by the default value for the specified LAMMPS
        unit system. 
    runsteps : int, optional
        How many timesteps the simulation will run for. Default value of 1,000,000
        should be suitable for a short run. 
    thermosteps : int, optional
        How often the calculated values get stored in the thermo table of the 
        LAMMPS output. Default value of 1,000.
    equilsteps : int, optional
        How many timesteps the equilibration simulation will run for. Default 
        value of 0.
    createvelocities : bool, optional
        Setting this to True will assign new random velocities to the atoms
        prior to running.  If this is used, then it would be wise to set an
        equilsteps value to let the velocities equilibrate before running the
        main Green-Kubo run.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities.  Only used
        if resetvelocities is True.  Default is None which will select a
        random int between 1 and 900000000.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:

        -**'viscosity_xy'** (*float*) - The calculated viscosity using only the
        Pxy pressures.
        -**'viscosity_xz'** (*float*) - The calculated viscosity using only the
        Pxz pressures.
        -**'viscosity_yz'** (*float*) - The calculated viscosity using only the
        Pyz pressures.
        -**'viscosity'** (*float*) - The calculated viscosity using all three
        shear pressures.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'viscosity_green_kubo.in'
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
    lmp.cmd.fix('nvt', 'all', 'nvt',
                'temp', temperature, temperature, temperature_damp)

    if createvelocities:
        lmp.commands_string('\n# Create new velocities')
        lmp.cmd.velocity('all', 'create', temperature, randomseed,
                         'mom', 'yes', 'rot', 'yes', 'dist', 'gaussian')

    lmp.commands_string('\n# Equilibration run')
    lmp.cmd.run(equilsteps)
    lmp.cmd.reset_timestep(0)
    lmp.cmd.unfix('nvt')

    lmp.cmd.fix('nve', 'all', 'nve')
    
    lmp.cmd.variable('pxy', 'equal', 'pxy')
    lmp.cmd.variable('pxz', 'equal', 'pxz')
    lmp.cmd.variable('pyz', 'equal', 'pyz')

    
    # Set thermo outputs
    lmp.cmd.thermo(1)
    lmp.cmd.thermo_style('custom', 'step', 'time', 'pxy', 'pxz', 'pyz')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Run for runsteps
    lmp.cmd.run(runsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
    thermo = log.simulations[1].thermo

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)

    # Analyze the results with the Green-Kubo tools
    volume = system.box.volume
    time = thermo.Time - thermo.Time.values[0]
    gkxy = am.thermo.GreenKuboMu(time, thermo.Pxy,
                                 temperature=temperature, volume=volume)
    gkxz = am.thermo.GreenKuboMu(time, thermo.Pxz,
                                 temperature=temperature, volume=volume)
    gkyz = am.thermo.GreenKuboMu(time, thermo.Pyz,
                                 temperature=temperature, volume=volume)

    # Identify integral cutoffs to use
    icutxy, tcutxy = gkxy.tcut_std_noise_fraction(15, threshold=.90)
    icutxz, tcutxz = gkxz.tcut_std_noise_fraction(15, threshold=.90)
    icutyz, tcutyz = gkyz.tcut_std_noise_fraction(15, threshold=.90)

    # Find the mu value at the cutoff index
    mu_xy = gkxy.mu()[icutxy]
    mu_xz = gkxz.mu()[icutxz]
    mu_yz = gkyz.mu()[icutyz]
    mu = (mu_xy + mu_xz + mu_yz) / 3

    # Generate plot of <P0*Pt> vs t for quality verification
    acf_units = 'MPa^2'
    time_units = 'ps'

    time = uc.get_in_units(gkxy.time, time_units)
    acfxy = uc.get_in_units(gkxy.acf, acf_units)
    acfxz = uc.get_in_units(gkxz.acf, acf_units)
    acfyz = uc.get_in_units(gkyz.acf, acf_units)
    plt.plot(time, acfxy, 'C1', label='xy')
    plt.plot(time, acfxz, 'C2', label='xz')
    plt.plot(time, acfyz, 'C3', label='yz')

    # Plot cutoff positions
    acfmax = np.max([acfxy, acfxz, acfyz])
    plt.plot([uc.get_in_units(tcutxy, time_units), uc.get_in_units(tcutxy, time_units)], [0.0, acfmax], 'C1:')
    plt.plot([uc.get_in_units(tcutxz, time_units), uc.get_in_units(tcutxz, time_units)], [0.0, acfmax], 'C2:')
    plt.plot([uc.get_in_units(tcutyz, time_units), uc.get_in_units(tcutyz, time_units)], [0.0, acfmax], 'C3:')

    plt.legend()
    plt.title('<P0*Pt> vs t')
    plt.xlabel('t (ps)')
    plt.xscale('log')
    plt.ylabel(f'<P0*Pt> (${acf_units}$)')
    plt.savefig('P0Pt.png')
    plt.close()

    results = {}
    results['thermo'] = thermo
    results['viscosity_xy'] = mu_xy
    results['viscosity_xz'] = mu_xz
    results['viscosity_yz'] = mu_yz
    results['viscosity'] = mu
    results['gkxy'] = gkxy
    results['gkxz'] = gkxz
    results['gkyz'] = gkyz

    return results