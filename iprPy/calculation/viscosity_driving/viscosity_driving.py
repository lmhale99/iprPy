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

def viscosity_driving(lammps_command:str,
              system: am.System,
              potential: lmp.Potential,
              temperature: float,
              mpi_command: Optional[str] = None,
              timestep: Optional[float] = None,
              drivingforce: float = .01,
              runsteps: int = 100000,
              thermosteps: int = 100,
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
    drivingforce : float, optional
        The amplitude of the driving force for the calculation method. Default 
        value of .01 - TBD. 
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

    #Raise Error if the values don't commute
    if (runsteps%(thermosteps) != 0):
        raise ValueError('Thermosteps must divide runsteps')

    #Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = uc.get_in_units(timestep,lammps_units['time'])

    lammps_variables['runsteps'] = runsteps
    lammps_variables['drivingforce'] = uc.get_in_units(drivingforce,f"{lammps_units['velocity']}/{lammps_units['time']}")
    lammps_variables['thermosteps'] = thermosteps

    #Setting up the seed 
    if randomseed is None:
        randomseed = random.randint(1,9000000)

    # Equilibrium steps
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
    lammps_script = 'in.viscosity.in'
    template = read_calc_file('iprPy.calculation.viscosity_driving',
                              'in.viscosity_driving.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))

    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="viscosity.log.lammps")
    
    thermo = output.simulations[-1].thermo

    #From thermo data calculate the Viscosity 
    runningTemperature = thermo["Temp"]
    avgTemp = np.average(runningTemperature)

    runningViscosityInverse = thermo["v_reciprocalViscosity"]
    
    avgInvVisc = np.average(runningViscosityInverse)
    stdInvVisc = np.std(runningViscosityInverse)
    # This is the correct way to average the data according to the "Harmonic Mean" 
    avgVisc = 1/avgInvVisc
    # This is the error propogation formula for f(x)=1/x 
    std_Visc = (avgVisc)*abs(stdInvVisc/avgInvVisc)

    #Unit Conversions According to the units in the lammps script 
    unitString = f"({lammps_units['length']}^3*{lammps_units['density']})/({lammps_units['velocity']}*{lammps_units['time']}^2)"

    #Initialize the return dictionary
    results = {}

    #Data of interest
    results['viscosity'] = uc.set_in_units(avgVisc,unitString)
    results['viscosity_stderr'] = uc.set_in_units(std_Visc/((len(runningViscosityInverse))**0.5),unitString)
    results['measured_temperature'] = uc.set_in_units(avgTemp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(np.std(runningTemperature[1:])/((len(runningTemperature[1:]))**0.5),'K')
    results['lammps_output'] = output    
    return results
 

