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

def viscosity_driving(lammps_command:str,
              potential: lmp.Potential,
              system: am.System,
              mpi_command: Optional[str] = None,
              temperature: float = 200,
              timestep: float = .5,
              runsteps: int = 100000,
              thermosteps: int = 100,
              drivingforce: float = .1,
              dataoffset: int = 500,
              randomseed: Optional[int] = None,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              dumpsteps: int = 0,
              directoryname: str = "dump"
              ) -> dict:
    
    #Get the Units from Potential
    lamps_units = lmp.style.unit(potential.units)

    #Initialize the variables to fill in the script
    lammps_variables = {}

    #Get the system info by loading the system into the init.dat and using the specified potential
    system_info = system.dump('atom_data',f='init.dat',potential = potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    #Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = timestep
    lammps_variables['runsteps'] = runsteps
    lammps_variables['drivingforce'] = drivingforce
    lammps_variables['thermosteps'] = thermosteps

    if randomseed is None:
        randomseed = random.randint(1,9000000)

    if (dumpsteps != 0) or (dumpsteps != None):
        mkdir(directoryname)
        instruct = f"""dump         dumpy all custom {dumpsteps} {directoryname}/*.dump id type x y z"""
        lammps_variables["Dump_instructions"] = instruct
    else:
        lammps_variables['Dump_instructions'] = ""

    # Equilibrium steps
    if eq_equilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} {randomseed} \n
                        thermo {eq_thermosteps} \n run {eq_runsteps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
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
    
    # Thermo index
    indexOffset = 0
    if eq_equilibrium: 
        indexOffset += 1

    #From thermo data calculate the Viscosity 
    log = lmp.Log('viscosity.log.lammps')
    runningViscosityInverse = log.simulations[indexOffset].thermo["v_reciprocalViscosity"]
    runningTemperature = log.simulations[indexOffset].thermo["Temp"]
    runningViscosity = np.array([1/i for i in runningViscosityInverse])
    Viscosity = np.average(runningViscosity[dataoffset:])
    AveTemp = np.average(runningTemperature[dataoffset:])
    #Unit Conversions
    unitString = "(" + lamps_units['length'] + "^3*"+ lamps_units['density'] + ")" + "/(" + lamps_units['velocity'] + "*" + lamps_units['time'] + "^2)"
    eta = uc.set_in_units(Viscosity,unitString)
    eta_std = uc.set_in_units(np.std(runningViscosity[dataoffset:]),unitString)

    #Initialize the return dictionary
    results = {}

    #Data of interest
    results['viscosity'] = eta
    results['viscosity_stderr'] = eta_std
    results['measured_temperature'] = AveTemp
    results['measured_temperature_stderr'] = np.std(runningTemperature[dataoffset:])
    results['lammps_output'] = output    
    return results
 
    
import os 
def mkdir(name):
    try:
        os.mkdir(name)
    except:
        print("Directory Already Exists - Please use a different name")
