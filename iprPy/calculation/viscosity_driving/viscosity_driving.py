# coding: utf-8
# Standard Python libraries
from typing import Optional

import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

import numpy as np 

from ...tools import read_calc_file

# Note - the system fed in needs to be relaxed to a liquid phase 
# otherwise the calculation doesn't make much sense and it needs to run for 
# significantly longer 

def viscosity_driving(lammps_command: str,
                      system: am.System,
                      potential: lmp.Potential,
                      temperature: float,
                      mpi_command: Optional[str] = None,
                      timestep: Optional[float] = None,
                      drivingforce: float = uc.set_in_units(2.0, 'angstrom/(ps^2)'),
                      runsteps: int = 100000,
                      thermosteps: int = 100,
                      equilsteps: int = 0,
                      ) -> dict:
    
    """
    Calculates the diffusion constant for a liquid system using
    the derivative of the mean squared displacement

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
        -**'lammps_output'** - The lammps output log
    """
    # Get the Units from Potential
    lammps_units = lmp.style.unit(potential.units)

    # Set default timestep based on units
    if timestep is None:
        timestep = uc.set_in_units(lmp.style.timestep(potential.units),
                                   lammps_units['time'])

    # Initialize the variables to fill in the script
    lammps_variables = {}

    # Get the system info by loading the system into the init.dat and using the specified potential
    system_info = system.dump('atom_data', f='init.dat', potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Raise Error if the values don't commute
    if (runsteps % (thermosteps) != 0):
        raise ValueError('thermosteps must divide runsteps')

    # Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['temperature'] = temperature
    lammps_variables['timestep'] = uc.get_in_units(timestep, lammps_units['time'])

    lammps_variables['runsteps'] = runsteps
    lammps_variables['drivingforce'] = uc.get_in_units(drivingforce, 
                                                       f"{lammps_units['velocity']} / {lammps_units['time']}")
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['thermosteps'] = thermosteps

    # Fill in the template 
    lammps_script = 'viscosity_driving.in'
    template = read_calc_file('iprPy.calculation.viscosity_driving',
                              'viscosity_driving.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
    
    thermo = output.simulations[-1].thermo

    # Compute mean and stderr of mean for temp
    measured_temps = thermo["Temp"].values
    measured_temp = np.average(measured_temps)
    measured_temp_stderr = np.std(measured_temps) / ((len(measured_temps) / 100) ** .5)

    # From thermo data calculate the viscosity
    inv_viscosities = thermo["v_reciprocalViscosity"]
    
    inv_viscosity = np.average(inv_viscosities)
    inv_viscosity_std = np.std(inv_viscosities)

    # This is the correct way to average the data according to the "Harmonic Mean" 
    viscosity = 1 / inv_viscosity
    
    # This is the error propagation formula for f(x)=1/x 
    viscosity_std = (viscosity) * abs(inv_viscosity_std / inv_viscosity)

    # Unit conversions according to the units in the lammps script 
    viscosity_unit = f"({lammps_units['length']}^3*{lammps_units['density']})/({lammps_units['velocity']}*{lammps_units['time']}^2)"

    # Initialize the return dictionary
    results = {}

    # Data of interest
    results['viscosity'] = uc.set_in_units(viscosity, viscosity_unit)
    results['viscosity_stderr'] = uc.set_in_units(viscosity_std / ((len(inv_viscosities))**0.5), viscosity_unit)
    results['measured_temperature'] = uc.set_in_units(measured_temp, 'K')
    results['measured_temperature_stderr'] = uc.set_in_units(measured_temp_stderr, 'K')
    results['lammps_output'] = output    
    return results
