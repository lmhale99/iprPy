# Python script created by Lucas Hale

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

def thermal_conductivity_green_kubo(lammps_command: Union[str, LAMMPSobj],
                                    system: am.System,
                                    potential: lammpspotential,
                                    temperature: float,
                                    mpi_command: Optional[str] = None,
                                    timestep: Optional[unitfloat] = None,
                                    equilsteps: int = 0,
                                    runsteps: int = 500000,
                                    centroid_stress: bool = False,
                                    createvelocities: bool = False,
                                    randomseed: Optional[int] = None,
                                    usefiles: bool = False) -> dict:
    """
    Computes the thermal conductivity of a system using the equilibrium
    Green-Kubo method.

    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to run at.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel. If not given, LAMMPS
        will run serially.
    timestep : float, optional
        The amount of time to increase each frame of the simulation. The 
        default value is given by the default value for the specified LAMMPS
        unit system. 
    equilsteps : int, optional
        How many timesteps the equilibration simulation will run for.  Default 
        value is 0.
    runsteps : int, optional
        How many timesteps the simulation will run for. Default value is 500,000.
    centroid_stress : bool, optional
        Changes which LAMMPS compute method is used for estimating the per-atom
        stress values: False (default) uses stress/atom, while True uses 
        centroid/stress/atom.
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
    ----------
    """

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'kappaGK.in'
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

    lmp.commands_string('\n# Set the timestep')
    lmp.cmd.timestep(timestep_lammps)

    # Optional equilibrium run
    if equilsteps > 0:
        assert temperature is not None

        if createvelocities:
            lmp.commands_string('\n# Create new velocities')
            lmp.cmd.velocity('all', 'create', temperature, randomseed, 'mom',
                            'yes', 'rot', 'yes', 'dist', 'gaussian')
        
        lmp.commands_string('\n# Equilibration run')
        lmp.cmd.fix('NVT', 'all', 'nvt', 'temp', temperature, temperature, temperature_damp)
        lmp.cmd.run(equilsteps)
        lmp.cmd.unfix('NVT')
        lmp.cmd.reset_timestep(0)

    lmp.commands_string('\n# Main simulation integrator definition')
    lmp.cmd.fix('NVE', 'all', 'nve')

    lmp.commands_string('\n# Set up heat/flux inputs computes')
    lmp.cmd.compute('myKE', 'all', 'ke/atom')
    lmp.cmd.compute('myPE', 'all', 'pe/atom')
    if centroid_stress:
        lmp.cmd.compute('myStress', 'all', 'centroid/stress/atom', 'NULL', 'virial')
    else:
        lmp.cmd.compute('myStress', 'all', 'stress/atom', 'NULL', 'virial')

    lmp.commands_string('\n# Set up heat/flux compute and output variables')
    lmp.cmd.compute('flux', 'all', 'heat/flux', 'myKE', 'myPE', 'myStress')
    lmp.cmd.variable('Jx', 'equal', 'c_flux[1]/vol')
    lmp.cmd.variable('Jy', 'equal', 'c_flux[2]/vol')
    lmp.cmd.variable('Jz', 'equal', 'c_flux[3]/vol')

    lmp.commands_string('\n# Set thermo outputs')
    thermo_keys = ['step', 'time', 'temp', 'vol', 'v_Jx', 'v_Jy', 'v_Jz']
    lmp.cmd.thermo_style('custom', *thermo_keys)
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    lmp.cmd.thermo(1)

    lmp.commands_string('\n# Run')
    lmp.cmd.run(runsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
    thermo = log.simulations[-1].thermo

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)

    # Convert units on flux terms
    flux_unit = f'{lmp.unitsdict["energy"]} / ({lmp.unitsdict["length"]}^2 * {lmp.unitsdict["time"]})'
    thermo.v_Jx = uc.set_in_units(thermo.v_Jx, flux_unit)
    thermo.v_Jy = uc.set_in_units(thermo.v_Jy, flux_unit)
    thermo.v_Jz = uc.set_in_units(thermo.v_Jz, flux_unit)
    
    # Pass results into the Green-Kubo solver
    volume = system.box.volume
    time = thermo.Time - thermo.Time.values[0]
    gkx = am.thermo.GreenKuboKappa(time, thermo.v_Jx, temperature=temperature, volume=volume)
    gky = am.thermo.GreenKuboKappa(time, thermo.v_Jy, temperature=temperature, volume=volume)
    gkz = am.thermo.GreenKuboKappa(time, thermo.v_Jz, temperature=temperature, volume=volume)

    # Identify integral cutoffs to use
    icutx, tcutx = gkx.tcut_std_noise_fraction(15, threshold=.90)
    icuty, tcuty = gky.tcut_std_noise_fraction(15, threshold=.90)
    icutz, tcutz = gkz.tcut_std_noise_fraction(15, threshold=.90)

    # Find the kappa value at the cutoff index
    kappax = gkx.kappa()[icutx]
    kappay = gky.kappa()[icuty]
    kappaz = gkz.kappa()[icutz]
    kappa = (kappax + kappay + kappaz) / 3

    # Generate plot of <J0*Jt> vs t for quality verification
    acf_units = 'eV^2*angstrom^2/ps^2'
    time_units = 'ps'

    time = uc.get_in_units(gkx.time, 'ps')
    acfx = uc.get_in_units(gkx.acf, acf_units)
    acfy = uc.get_in_units(gky.acf, acf_units)
    acfz = uc.get_in_units(gkz.acf, acf_units)

    plt.plot(time, acfx, 'C1', label='x')
    plt.plot(time, acfy, 'C2', label='y')
    plt.plot(time, acfz, 'C3', label='z')

     # Plot cutoff positions
    acfmax = np.max([acfx, acfy, acfz])
    plt.plot([uc.get_in_units(tcutx, time_units), uc.get_in_units(tcutx, time_units)], [0.0, acfmax], 'C1:')
    plt.plot([uc.get_in_units(tcuty, time_units), uc.get_in_units(tcuty, time_units)], [0.0, acfmax], 'C2:')
    plt.plot([uc.get_in_units(tcutz, time_units), uc.get_in_units(tcutz, time_units)], [0.0, acfmax], 'C3:')

    plt.legend()
    plt.title('<J0*Jt> vs t')
    plt.xlabel('t (ps)')
    plt.xscale('log')
    plt.ylabel(f'<J0*Jt> (${acf_units}$)')
    plt.savefig('J0Jt.png')
    plt.close()

    # Save values to results dictionary
    results_dict = {}
    results_dict['gkx'] = gkx
    results_dict['gky'] = gky
    results_dict['gkz'] = gkz
    results_dict['kappax'] = kappax
    results_dict['kappay'] = kappay
    results_dict['kappaz'] = kappaz
    results_dict['kappa'] = kappa
    
    return results_dict
