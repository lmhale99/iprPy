
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

def diffusion_liquid(lammps_command:str,
                     system: am.System,
                     potential: lmp.Potential,
                     temperature: float,
                     mpi_command: Optional[str] = None,
                     timestep: Optional[float] = None,
                     runsteps: int = 50000,
                     simruns: int = 10,
                     equilsteps: int = 0,
                     ) -> dict:
    """
    Calculates the diffusion constant for a liquid system using
    the integral of the velocity autocorrelation function

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
    runsteps : int, optional
        How many timesteps each simulation will run for. Default value is 50000. 
    simruns : int, optional
        The number of simulations to run. The higher the number the less noise
        in the VACF calculation. Default value of 10.
    equilsteps : int, optional
        How many timesteps the equilibiration simulation will run for. Default 
        value of 0.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:

        -**'vacf_x_values'** (*Numpy array of floats*) - The array of 
        calculated x components of the msd values
        -**'vacf_y_values'** (*Numpy array of floats*) - The array of 
        calculated y components of the msd values
        -**'vacf_z_values'** (*Numpy array of floats*) - The array of 
        calculated z components of the msd values
        -**'vacf_values'** (*Numpy array of floats*) - The array of 
        calculated msd values
        -**'measured_temperature'** (*float*) - The average measured
        temperature of the system ignore initial data according to 
        the data offset.
        -**'measured_temperature_stderr'** (*float*) - The standard 
        deviation measured temperature of the system ignore initial 
        data according to the data offset.
        -**'diffusion'** (*float*) - The calculated diffusion 
        coeffecient
        -**'diffusion_stderr'** (*float*) - The standard deviation
        of the diffusion coeffecient
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

    # Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['temperature'] = temperature
    lammps_variables['timestep'] = uc.get_in_units(timestep, lammps_units['time'])
    lammps_variables['runsteps'] = runsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['num_simulations'] = simruns

    #Fill in the template
    lammps_script = 'diffusion_liquid.in'
    template = read_calc_file('iprPy.calculation.diffusion_liquid',
                              'diffusion_liquid.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    #Run lamps
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
    
    # Init lists of values
    diffusion_vacf_values = []
    diffusion_msd_short_values = []
    measured_temps = []
    msd_long_running = []
    steps_long_running = []

    msd_unit = f"{lammps_units['length']}^2"
    diffusion_msd_unit = f"{lammps_units['length']}^2/{lammps_units['time']}"
    diffusion_vacf_unit = f"{lammps_units['velocity']}^2*{lammps_units['time']}"

    for i in range(1, simruns+1):
        thermo = output.simulations[i].thermo

        # Get last diffusion values for short MSD and VACF
        diffusion_vacf_values.append(thermo['v_eta'].values[-1])
        diffusion_msd_short_values.append(thermo['v_fitslopeShort'].values[-1])
        
        # Append lists with all long MSD, steps, and temperature measurements
        msd_long_running += thermo['c_msdLong[4]'].tolist()
        steps_long_running += thermo['Step'].tolist()
        measured_temps += thermo['Temp'].tolist()

    # Get long MSD estimate from the last simulation
    thermo = output.simulations[-1].thermo
    diffusion_msd_long_value = uc.set_in_units(thermo['v_fitslopeLong'].values[-1], 
                                               diffusion_msd_unit)

    # Unit convert MSD and diffusion values
    diffusion_vacf_values = uc.set_in_units(diffusion_vacf_values, diffusion_vacf_unit)
    diffusion_msd_short_values = uc.set_in_units(diffusion_msd_short_values, diffusion_msd_unit)
    msd_long_running = uc.set_in_units(msd_long_running, msd_unit)
    time_running = np.array(steps_long_running) * timestep

    # Compute error associated with linear fit for MSD long
    #temp_error_sum = 0
    #for i in range(len(msd_long_running)):
    #    temp_error_sum += (msd_long_running[i] - (diffusion_msd_long_value*2*3*timestep))**2 
        #Note the 2 and 3 come from the diffusion formula 
    #diffusion_msd_long_stderr = temp_error_sum / len(msd_long_running)
    diffusion_msd_long_stderr = (np.sum((msd_long_running[1:] / (6 * time_running[1:]) - diffusion_msd_long_value)**2) / len(msd_long_running)) ** 0.5

    # Compute mean and stderr of mean for temp, VACF and MSD short
    measured_temp = np.average(measured_temps)
    measured_temp_stderr = np.std(measured_temps) / ((len(measured_temps) / 100) ** .5)
    
    diffusion_msd_short_value = np.average(diffusion_msd_short_values)
    diffusion_msd_short_stderr = np.std(diffusion_msd_short_values) / (simruns ** .5)
    
    diffusion_vacf_value = np.average(diffusion_vacf_values)
    diffusion_vacf_stderr = np.std(diffusion_vacf_values) / (simruns ** .5)

    # Build results dict
    results = {}
    results['diffusion_msd_short'] = diffusion_msd_short_value
    results['diffusion_msd_short_stderr'] = diffusion_msd_short_stderr
    results['diffusion_msd_long'] = diffusion_msd_long_value
    results['diffusion_msd_long_stderr'] = diffusion_msd_long_stderr
    results['diffusion_vacf'] = diffusion_vacf_value
    results['diffusion_vacf_stderr'] = diffusion_vacf_stderr
    results['measured_temperature'] = measured_temp
    results['measured_temperature_stderr'] = measured_temp_stderr
    
    results['lammps_output'] = output 
    return results
    
    