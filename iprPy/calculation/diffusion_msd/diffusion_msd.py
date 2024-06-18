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

def diffusion_msd(lammps_command:str, 
              potential: lmp.Potential,         
              system: am.System,                
              randomseed: Optional[int] = None,
              mpi_command: Optional[str] = None,
              temperature: float = 200,         
              timestep: float = .5,             
              dumpsteps: int = 0,
              directoryname: str = "dump",          
              runsteps: int = 100000,         
              thermosteps: int = 1000,        
              dataoffset: int = 500,          
              degrees_freedom: int = 3,       
              eq_thermosteps: int = 0,        
              eq_runsteps: int = 0,           
              eq_equilibrium: bool = False,   
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
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Thermo_Steps'] = thermosteps
    lammps_variables['Degrees_freedom'] = degrees_freedom
    
    # Setting up the dump instructions
    if (dumpsteps != 0) or (dumpsteps != None):
        mkdir(directoryname)
        instruct = f"""dump	        dumpy all custom {dumpsteps} {directoryname}/*.dump id type x y z"""
        lammps_variables["Dump_instructions"] = instruct
    else:
        lammps_variables['Dump_instructions'] = ""

    # Set up the seed 
    if randomseed is None:
        randomseed = random.randint(1,9000000)

    #Setting up equilbrium run
    if eq_equilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} {randomseed} \n
                        thermo {eq_thermosteps} \n run {eq_runsteps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_equilibrium or eq_runsteps == 0:
        lammps_variables['Equilibration_instructions'] = ""
        

    #Fill in the template 
    lammps_script = 'in.diffusion.in'
    template = read_calc_file('iprPy.calculation.diffusion_msd',
                              'in.diffusion_msd.template')
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    # Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile='diffusion_msd.log.lammps')
    
    results = {}

    thermo_index = 0
    if eq_equilibrium:
        thermo_index += 1

    log = lmp.Log('diffusion_msd.log.lammps')
    runningDiffusion = log.simulations[thermo_index].thermo['v_fitslope']
    runningTemperature = log.simulations[thermo_index].thermo['Temp']
    runningMSD = log.simulations[thermo_index].thermo['c_msd[4]']

    runningMSD_x = log.simulations[thermo_index].thermo['c_msd[1]']
    runningMSD_y = log.simulations[thermo_index].thermo['c_msd[2]']
    runningMSD_z = log.simulations[thermo_index].thermo['c_msd[3]']


    Diffusion_coeff = np.average(runningDiffusion[dataoffset:])

    AveTemp = np.average(runningTemperature[dataoffset:])
    AveMSD = np.average(runningMSD[dataoffset:])
    #unit conversions 
    unitString1 = f"({lamps_units['length']}^2)/({lamps_units['time']})"

    unitString2 = f"({lamps_units['length']}^2)"
    D = uc.set_in_units(Diffusion_coeff,unitString1)
    
    MSD = uc.set_in_units(AveMSD,unitString2)

    results['msd_x_values'] = runningMSD_x 
    results['msd_y_values'] = runningMSD_y 
    results['msd_z_values'] = runningMSD_z 
    results['msd_values'] = MSD 
    results['measured_temperature'] = AveTemp
    results['measured_temperature_stderror'] = np.std(runningTemperature[dataoffset:])
    results['diffusion'] = D
    results['diffusion_stderror'] = np.std(runningDiffusion[dataoffset:])
    results['lammps_output'] = output 

    return results
    
import os 
def mkdir(name):
    try:
        os.mkdir(name)
    except:
        print("Directory Already Exists - Please use a different name")

    