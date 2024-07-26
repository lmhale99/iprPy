#current in 6/11/24 - duplicated in working directoy

from pathlib import Path 
import random
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

def diffusion(lammps_command:str,
              system: am.System,
              potential: lmp.Potential,
              temperature: float,
              mpi_command: Optional[str] = None,
              timestep: Optional[float] = None,
              runsteps: int = 10000,
              simruns: int = 5,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              randomseed: Optional[int] = None
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
        The MPI command for running LAMMPS in paralell. If not given, LAMMPS
        will run serially.
    timestep : float, optional
        The amount of time to increase each frame of the simulation. The 
        default value is given by the default value for the specified LAMMPS
        unit system. 
    runsteps : int, optional
        How many timesteps the simulation will run for. Default value of 100,000
        should be suitable for a short run. 
    simruns : int, optional
        The number of simulations to run. The higher the number the less noise
        in the calculation. Default value of 5.
    eq_thermosteps : int, optional
        How often the calculated values of the equilibirum run get stored in 
        the thermo table of the LAMMPS output. Default value of 0.  
    eq_runsteps : int, optional
        How many timesteps the equilibiration simulation will run for. Default 
        value of 0.
    eq_equilibrium : bool, optional
        Dictates whether to run an equilibration simulation before the calculation
        simulation. Default value is false. 
    randomseed : int, optional,
        The randomseed for velocity assignment in an equilibration run. Default 
        value of None will result in a number being chosen at random from the 
        python random package.  
    
    
    Returns
    -------
    dict
        Dictionary of resutls consisting of keys:

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
    #Get the Units from Potential
    lammps_units = lmp.style.unit(potential.units)

    # Set default timestep based on units
    if timestep is None:
        timestep = lmp.style.timestep(potential.units)

    #Initialize the variables to fill in the script
    lammps_variables = {}

    #Get the system info by loading the system into the init.dat and using the specified potential
    system_info = system.dump('atom_data',f='init.dat',potential = potential)
    lammps_variables['atomman_system_pair_info'] = system_info




    #Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = uc.get_in_units(timestep,lammps_units['time'])
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Equilibration_thermo'] = eq_thermosteps
    lammps_variables['Equilibration_steps'] = eq_runsteps
    lammps_variables['num_simulations'] = simruns
    lammps_variables['Degrees_freedom'] = 3

    #Set up the seed
    if randomseed is None:
        randomseed = random.randint(1,9000000)

    #Setting up equilbrium
    if eq_equilibrium:
        instruct = '\n'.join([
            "fix NVE all nve",
            f"fix LANGEVIN all langevin $T $T {10*timestep} {randomseed}",
            f"thermo {eq_thermosteps}",
            f"run {eq_runsteps}",
            "unfix NVE",
            "unfix LANGEVIN",
            "reset_timestep 0"])
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_equilibrium or eq_runsteps == 0:
        lammps_variables['Equilibration_instructions'] = ""

    #Fill in the template
    lammps_script = 'in.diffusion.in'
    template = read_calc_file('iprPy.calculation.diffusion_vacf',
                              'in.diffusion_vacf.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="diffusion.log.lammps")
    
    results = {}

    indexOffset = 0
    if eq_equilibrium: 
        indexOffset += 1

    log = lmp.Log('diffusion.log.lammps')

    diffusion_vacf_values = []
    diffusion_msd_short_values = []
    diffusion_msd_long_value = 0
    measured_temps = []


    msd_long_running = []
    steps_long_running = []

    for i in range(indexOffset,simruns+indexOffset):
        # Iterating through the different simulations
        # Want to take the the last values for each run for 
        # fitslopeShort and eta, only want the very last value
        # for fitslopeLong
        diffusion_vacf_values.append(log.simulations[i].thermo['v_eta'][-1])
        diffusion_msd_short_values.append(log.simulations[i].thermo['v_fitslopeShort'][-1])
        msd_long_running += log.simulations[i].thermo['c_msdLong[4]']
        steps_long_running += log.simulations[i].thermo['Step']
        measured_temps.append(log.simulations[i].termo['Temp'])

        if (i == simruns+indexOffset-1):
            msd_long_value = log.simulations[i].thermo['v_fitslopeLong']

    # The error for the vacf and msd_short values will just be the standard method
    # The error for msd_long will be the error associated with the linear fit
    # Error calculation for msd_long calculation
    temp_error_sum = 0
    for i in range(len(msd_long_running)):
        temp_error_sum += (msd_long_running[i]-(diffusion_msd_long_value*2*3*timestep))**2 
        #Note the 2 and 3 come from the diffusion formula 

    diffusion_msd_long_stderr = temp_error_sum/len(msd_long_running)
    diffusion_msd_short_stderr = np.std(diffusion_msd_short_values)/((len(diffusion_msd_short_values))**(.5))
    diffusion_vacf_stderr = np.std(diffusion_vacf_values)/((len(diffusion_vacf_values))**(.5))

    diffusion_vacf_value = np.average(diffusion_vacf_values)
    diffusion_msd_short_value = np.average(diffusion_msd_short_values)

    measured_temp = np.average(measured_temps)
    measured_temp_stderr = np.std(measured_temps)/((len(measured_temps))**(.5))

    diffusionUnitString = f'{lammps_units['velocity']}^2*{lammps_units['time']}'

    results['diffusion_msd_short'] = uc.set_in_units(diffusion_msd_short_value,diffusionUnitString)
    results['diffusion_msd_short_stderr'] = uc.set_in_units(diffusion_msd_short_stderr,diffusionUnitString)

    results['diffusion_msd_long'] = uc.set_in_units(diffusion_msd_long_value,diffusionUnitString)
    results['diffusion_msd_long_stderr'] = uc.set_in_units(diffusion_msd_long_stderr,diffusionUnitString)

    results['diffusion_vacf'] = uc.set_in_units(diffusion_vacf_value,diffusionUnitString)
    results['diffusion_vacf_stderr'] = uc.set_in_units(diffusion_vacf_stderr,diffusionUnitString)

    results['measured_temperature'] = uc.set_in_units(measured_temp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(measured_temp_stderr,'K')
    
    results['lammps_output'] = output 
    return results
    
    