import datetime 
import random
from typing import Optional

import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

import numpy as np 

# Note - the system fed in needs to be relaxed to a liquid phase 
# otherwise the calculation doesn't make much sense and it needs to run for 
# significantly longer 

def viscosity_calc(lammps_command:str,
              potential: lmp.Potential,
              system: am.System,
              mpi_command: Optional[str] = None,
              temperature: float = 200,
              timestep: float = .5,
              correlation_length: int = 400,
              sample_interval: int = 5,
              dump_steps: int = 2000,
              run_steps: int = 100000,
              Thermo_steps: int = 100,
              driving_force: float = .1,
              Data_step: int = 500
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
    lammps_variables['Correlation_Length'] = correlation_length
    lammps_variables['Sample_Interval'] = sample_interval
    lammps_variables['Run_length'] = run_steps
    lammps_variables['Driving_Force'] = driving_force
    lammps_variables['Thermo_Steps'] = Thermo_steps
    lammps_variables['Dump_Interval'] = dump_steps
    #Fill in the template 
    lammps_script = 'in.viscosity.in'
    with open("in.viscosity_driving.template",'r') as template_f:
        with open(lammps_script,'w') as f:
            f.write(filltemplate(template_f,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="viscosity.log.lammps")
    
    #From thermo data calculate the Viscosity 
    log = lmp.Log('viscosity.log.lammps')
    runningViscosityInverse = log.simulations[0].thermo["v_reciprocalViscosity"]
    runningTemperature = log.simulations[0].thermo["Temp"]
    runningViscosity = np.array([1/i for i in runningViscosityInverse])
    Viscosity = np.average(runningViscosity[Data_step:])
    AveTemp = np.average(runningTemperature[Data_step:])
    #Unit Conversions
    unitString = "(" + lamps_units['length'] + "^3*"+ lamps_units['density'] + ")" + "/(" + lamps_units['velocity'] + "*" + lamps_units['time'] + "^2)"
    eta = uc.set_in_units(Viscosity,unitString)

    #Initialize the return dictionary
    results = {}
    # thermo = output.flatten()['thermo']
    #Data of interest
    results['dumpfile_initial'] = '0.dump'
    results['symbols_initial'] = system.symbols
    results['viscosity'] = eta
    results['temperature'] = AveTemp
    #Other Dump Data
    print(eta)    
    return results
 
    

    