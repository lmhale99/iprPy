import datetime 
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

def viscosity_green_kubo(lammps_command:str,
              system: am.System,
              potential: lmp.Potential,
              temperature: float,
              mpi_command: Optional[str] = None,
              timestep: Optional[float] = None,
              correlationlength: int = 400,
              sampleinterval: int = 5,
              outputsteps: int = 2000,
              runsteps: int = 100000,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              dragcoeff: float = .01,
              randomseed: Optional[int] = None
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
    directoryname : str, optional
        If you wish to write to a dump file this is the name of the folder in 
        which the files will be created. 
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

    #Conversion tools

    #Get the boltzman constant in si
    kb_SI = uc.set_in_units(1.3806504*(10**(-23)),"(kg*m^2)/(s^2*K)")

    #Account for /mole unit
    mass_unit = lammps_units['mass']
    if mass_unit == "g/mol": mass_unit = 'g'

    #Get boltzman in new unit system
    unitStringKB = f"({mass_unit}*{lammps_units['length']}^2)/({lammps_units['time']}^2*{lammps_units['temperature']})"
    kb = uc.get_in_units(kb_SI,unitStringKB)

    #Conversion factor from dimensions of pressure to working calculation units
    unitStringScale = f"({mass_unit})/({lammps_units['length']}*{lammps_units['time']}^2)"
    scale_unit = uc.set_in_units(1,f"{lammps_units['pressure']}")
    scale = uc.get_in_units(scale_unit,unitStringScale)
 

    #Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = timestep
    lammps_variables['Correlation_Length'] = correlationlength
    lammps_variables['Sample_Interval'] = sampleinterval
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Dump_Interval'] = outputsteps
    lammps_variables['Boltzman_constant'] = kb
    lammps_variables['Scale'] = scale 
    lammps_variables['Drag_coeff'] = dragcoeff 

    if randomseed is None:
        randomseed = random.randint(1,9000000)

    #Setting up equibilrium run 
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
    template = read_calc_file('iprPy.calculation.viscosity_green_kubo',
                              'in.viscosity_green_kubo.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="viscosity.log.lammps")
    
    thermo = output.simulations[-1].thermo

    #From thermo data calculate the Viscosity 
    runningViscosity = thermo["v_v"]
    runningTemperature = thermo["Temp"]

    running_pxy = thermo['v_pxy']
    running_pxz = thermo['v_pxz']
    running_pyz = thermo['v_pyz']

    running_vx = thermo['v_v11']
    running_vy = thermo['v_v22']
    running_vz = thermo['v_v33']

    Viscosity = np.average(runningViscosity[1:])
    AveTemp = np.average(runningTemperature[1:])

    viscosityUnitString = f'{lammps_units['pressure']}*{lammps_units['time']}'
    pressureUnitString = f'{lammps_units['pressure']}'
    #Initialize the return dictionary
    results = {}
    #Data of interest
    results['viscosity_stderr'] = uc.set_in_units(np.std(runningViscosity[1:])/((len(runningViscosity))**0.5),viscosityUnitString)
    results['viscosity'] = uc.set_in_units(Viscosity,viscosityUnitString)
    results['measured_temperature'] = uc.set_in_units(AveTemp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(np.std(runningTemperature[1:])/((len(runningTemperature))**0.5),'K')

    results['pxy_values'] = uc.set_in_units(running_pxy[1:],pressureUnitString)
    results['pxz_values'] = uc.set_in_units(running_pxz[1:],pressureUnitString)
    results['pyz_values'] = uc.set_in_units(running_pyz[1:],pressureUnitString)

    results['vx_value'] = uc.set_in_units(np.average(running_vx[1:]),viscosityUnitString)
    results['vy_value'] = uc.set_in_units(np.average(running_vy[1:]),viscosityUnitString)
    results['vz_value'] = uc.set_in_units(np.average(running_vz[1:]),viscosityUnitString)

    results['lammps_output'] = output
    return results