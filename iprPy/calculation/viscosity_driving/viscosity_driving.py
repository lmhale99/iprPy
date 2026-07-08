# Python script created by Peter Winstel and Lucas Hale

# Standard Python libraries
from typing import Optional, Union

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def viscosity_driving(lammps_command: Union[str, LAMMPSobj],
                      system: am.System,
                      potential: lammpspotential,
                      temperature: float,
                      mpi_command: Optional[str] = None,
                      timestep: Optional[unitfloat] = None,
                      drivingforce: unitfloat = '2.0 angstrom/(ps^2)',
                      runsteps: int = 100000,
                      thermosteps: int = 100,
                      equilsteps: int = 0,
                      createvelocities: bool = False,
                      randomseed: Optional[int] = None,
                      usefiles: bool = False) -> dict:
    
    """
    Calculates the viscosity for a liquid system by applying a driving
    force.

    Parameters
    ----------
    lammps_command : str
        Command for running LAMMPS
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
    drivingforce : float, optional
        The amplitude of the driving force for the calculation method. Default 
        value is 2 angstrom/(ps^2). 
    runsteps : int, optional
        How many timesteps the simulation will run for. Default value of 100,000
        should be suitable for a short run. 
    thermosteps : int, optional
        How often the calculated values get stored in the thermo table of the 
        LAMMPS output. Default value of 1,000. 
    equilsteps : int, optional
        How many timesteps the equilibration simulation will run for. Default 
        value of 0.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:

        -**'measured_temperature'** (*float*) - The average measured
        temperature of the system ignore initial data according to 
        the data offset.
        -**'measured_temperature_stderr'** (*float*) - The standard 
        deviation measured temperature of the system ignore initial 
        data according to the data offset.
        -**'viscosity'** (*float*) - The calculated viscosity 
        -**'viscosity_stderr'** (*float*) - The standard deviation
        of the viscosity
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'viscosity_driving.in'
    else:
        script = None

    # Convert values given with units if needed
    drivingforce = uc.set_in_units(drivingforce)

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

    lmp.commands_string('\n# Set up the applied perturbation')
    drivingforce_units = f"{lmp.unitsdict['velocity']}/{lmp.unitsdict['time']}"
    lmp.cmd.variable('A', 'equal', uc.get_in_units(drivingforce, 
                                                   drivingforce_units))
    lmp.cmd.fix('cos', 'all', 'accelerate/cos', '${A}')
    lmp.cmd.compute('cos', 'all', 'viscosity/cos')
    lmp.cmd.variable('vMax', 'equal', 'c_cos[7]')
    lmp.cmd.fix_modify('nvt', 'temp', 'cos')

    lmp.commands_string('\n# Define calculation terms')
    lmp.cmd.variable('density', 'equal', 'density')
    lmp.cmd.variable('lz', 'equal', 'lz')
    lmp.cmd.variable('reciprocalViscosity', 'equal', 'v_vMax/${A}/v_density*39.4784/v_lz/v_lz')

    lmp.commands_string('\n# Set thermo outputs')
    lmp.cmd.thermo_style('custom', 'step', 'cpu', 'temp', 'press', 'pe', 'density', 'v_vMax', 'v_reciprocalViscosity')
    lmp.cmd.thermo_modify('temp', 'cos')
    lmp.cmd.thermo(thermosteps)

    lmp.commands_string('\n# Run for runsteps')
    lmp.cmd.run(runsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
    
    thermo = log.simulations[-1].thermo

    sqrt_nsamples = len(thermo) ** 0.5

    # Compute mean and stderr of mean for temp
    measured_temps = thermo["Temp"].values
    measured_temp = measured_temps.mean()
    measured_temp_stderr = measured_temps.std() / sqrt_nsamples

    # From thermo data calculate the viscosity
    inv_viscosities_units = f"{lmp.unitsdict['time']}/({lmp.unitsdict['density']}*{lmp.unitsdict['length']}^2)"
    inv_viscosities = uc.set_in_units(thermo["v_reciprocalViscosity"].values,
                                      inv_viscosities_units)
    
    inv_viscosity = inv_viscosities.mean()
    inv_viscosity_std = inv_viscosities.std()

    # This is the correct way to average the data according to the "Harmonic Mean" 
    viscosity = 1 / inv_viscosity
    
    # This is the error propagation formula for f(x)=1/x 
    viscosity_std = (viscosity) * abs(inv_viscosity_std / inv_viscosity)

    # Initialize the return dictionary
    results = {}

    # Data of interest
    results['viscosity'] = viscosity
    results['viscosity_stderr'] = viscosity_std / sqrt_nsamples
    results['measured_temperature'] = measured_temp
    results['measured_temperature_stderr'] = measured_temp_stderr

    return results
