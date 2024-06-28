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

def diffusion_msd(lammps_command: str, 
                  system: am.System,
                  potential: lmp.Potential,
                  temperature: float,
                  mpi_command: Optional[str] = None,
                  timestep: Optional[float] = None,
                  runsteps: int = 100000,
                  thermosteps: int = 1000,
                  eq_thermosteps: int = 0,
                  eq_runsteps: int = 0,
                  eq_equilibrium: bool = False,
                  randomseed: Optional[int] = None,  
                  ) -> dict:
    
    """
    Calculates the diffusion constant for a liquid system using
    the derivative of the mean squared displacment

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
    thermosteps : int, optional
        How often the calculated values get stored in the thermo table of the 
        LAMMPS output. Default value of 1,000.
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

        -**'msd_x_values'** (*Numpy array of floats*) - The array of 
        calculated x components of the msd values
        -**'msd_y_values'** (*Numpy array of floats*) - The array of 
        calculated y components of the msd values
        -**'msd_z_values'** (*Numpy array of floats*) - The array of 
        calculated z components of the msd values
        -**'msd_values'** (*Numpy array of floats*) - The array of 
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
        timestep = lmp.style.timestep(potential.units)

    # Initialize the variables to fill in the script
    lammps_variables = {}

    # Get the system info by loading the system into the init.dat and using the specified potential
    system_info = system.dump('atom_data', f='init.dat', potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = uc.set_in_units(timestep,lammps_units['time'])
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Thermo_Steps'] = thermosteps
    lammps_variables['Degrees_freedom'] = 3 #Fixed value 
    

    # Set up the seed 
    if randomseed is None:
        randomseed = random.randint(1, 9000000)

    # Setting up equilibrium run
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
        

    # Fill in the template 
    lammps_script = 'in.diffusion.in'
    template = read_calc_file('iprPy.calculation.diffusion_msd',
                              'in.diffusion_msd.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    # Run lammps
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False, 
                     logfile='diffusion_msd.log.lammps')
    
    thermo = output.simulations[-1].thermo

    results = {}

    runningDiffusion = thermo['v_fitslope']
    runningTemperature = thermo['Temp']
    runningMSD = thermo['c_msd[4]']

    runningMSD_x = thermo['c_msd[1]']
    runningMSD_y = thermo['c_msd[2]']
    runningMSD_z = thermo['c_msd[3]']

    Diffusion_coeff = np.average(runningDiffusion[1:])

    AveTemp = np.average(runningTemperature[1:])
    MSD_unitless = (runningMSD[1:])
    
    # unit conversions 
    length2_per_time_unit = f"({lammps_units['length']}^2)/({lammps_units['time']})"
    length2_unit = f"({lammps_units['length']}^2)"

    results['msd_x_values'] = uc.set_in_units(runningMSD_x,length2_unit) 
    results['msd_y_values'] = uc.set_in_units(runningMSD_y,length2_unit)
    results['msd_z_values'] = uc.set_in_units(runningMSD_z,length2_unit)
    results['msd_values'] = uc.set_in_units(MSD_unitless,length2_unit) 
    results['measured_temperature'] = uc.set_in_units(AveTemp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(np.std(runningTemperature[1:])/((len(runningTemperature[1:]))**0.5),'K')
    results['diffusion'] = uc.set_in_units(Diffusion_coeff, length2_per_time_unit)
    results['diffusion_stderr'] = uc.set_in_units(np.std(runningDiffusion[1:])/((len(runningDiffusion[1:]))**0.5),length2_per_time_unit)
    results['lammps_output'] = output 

    return results
    