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

def viscosity_green_kubo(lammps_command:str,
                         system: am.System,
                         potential: lmp.Potential,
                         temperature: float,
                         mpi_command: Optional[str] = None,
                         timestep: Optional[float] = None,
                         correlationlength: int = 200,
                         sampleinterval: int = 5,
                         outputsteps: int = 2000,
                         runsteps: int = 1000000,
                         equilsteps: int = 0,
                         dragcoeff: float = 0.2,
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
        value of 0.2. 
    runsteps : int, optional
        How many timesteps the simulation will run for. Default value of 1,000,000
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
    # Get the units from Potential
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

    # Conversion tools

    # Get the Boltzmann constant in si
    kB_SI = uc.set_in_units(1.3806504*(10**(-23)),"(kg*m^2)/(s^2*K)")

    # Account for /mole unit
    mass_unit = lammps_units['mass']
    if mass_unit == "g/mol": 
        mass_unit = 'g'

    # Get the Boltzmann constant in the LAMMPS unit system
    lammps_kB_unit = f"({mass_unit}*{lammps_units['length']}^2)/({lammps_units['time']}^2*{lammps_units['temperature']})"
    kB_lammps = uc.get_in_units(kB_SI, lammps_kB_unit)

    # Conversion factor from dimensions of pressure to working calculation units
    scale_unit_str = f"({mass_unit})/({lammps_units['length']}*{lammps_units['time']}^2)"
    scale_unit = uc.set_in_units(1, f"{lammps_units['pressure']}")
    scale = uc.get_in_units(scale_unit, scale_unit_str)
 
    # Raise Error if the values don't commute
    if (runsteps % (outputsteps) != 0):
        raise ValueError('thermosteps must divide runsteps')

    # Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['temperature'] = temperature
    lammps_variables['timestep'] = uc.get_in_units(timestep, lammps_units['time'])
    lammps_variables['correlationlength'] = correlationlength
    lammps_variables['sampleinterval'] = sampleinterval
    lammps_variables['runsteps'] = runsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['outputsteps'] = outputsteps
    lammps_variables['kB'] = kB_lammps
    lammps_variables['convert'] = scale 
    lammps_variables['dragcoeff'] = dragcoeff 

    # Fill in the template
    lammps_script = 'viscosity_green_kubo.in'
    template = read_calc_file('iprPy.calculation.viscosity_green_kubo',
                              'viscosity_green_kubo.template')
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

    # Extract viscosity and pressure values from thermo
    viscosity_unit = f"{lammps_units['pressure']}*{lammps_units['time']}"
    pressure_unit = lammps_units['pressure']

    viscosities = uc.set_in_units(thermo["v_v"].values, viscosity_unit)

    pressures_xy = uc.set_in_units(thermo['v_pxy'].values, pressure_unit)
    pressures_xz = uc.set_in_units(thermo['v_pxz'].values, pressure_unit)
    pressures_yz = uc.set_in_units(thermo['v_pyz'].values, pressure_unit)

    viscosities_x = uc.set_in_units(thermo['v_v11'].values, viscosity_unit)
    viscosities_y = uc.set_in_units(thermo['v_v22'].values, viscosity_unit)
    viscosities_z = uc.set_in_units(thermo['v_v33'].values, viscosity_unit)

    # Viscosity measurement is the final value of the integral
    viscosity = viscosities[-1] 
    
    # Initialize the return dictionary
    results = {}

    # Data of interest
    results['viscosity'] = viscosity
    results['viscosity_stderr'] = 0.0   # There is no notion of error for the Green-Kubo Calculation Method
    
    results['measured_temperature'] = measured_temp
    results['measured_temperature_stderr'] = measured_temp_stderr

    results['pxy_values'] = pressures_xy
    results['pxz_values'] = pressures_xz
    results['pyz_values'] = pressures_yz

    results['vx_value'] = np.average(viscosities_x[1:])
    results['vy_value'] = np.average(viscosities_y[1:])
    results['vz_value'] = np.average(viscosities_z[1:])

    results['lammps_output'] = output
    return results
