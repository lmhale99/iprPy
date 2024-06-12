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

def calculate_diffusion_msd(lammps_command:str,
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
              Data_step: int = 500,
              Degrees_freedom: int = 3,
              eq_Thermo_steps: int = 0,
              eq_Run_steps: int = 0,
              eq_Equibilibrium: bool = False,
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
    lammps_variables['Thermo_Steps'] = Thermo_steps
    lammps_variables['Dump_Interval'] = dump_steps
    lammps_variables['Degrees_freedom'] = Degrees_freedom
    
    #Setting up equilbrium run
    if eq_Equibilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} 498094 \n
                        thermo {eq_Thermo_steps} \n run {eq_Run_steps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_Equibilibrium or eq_Run_steps == 0:
        lammps_variables['Equilibration_instructions'] = ""
        

    #Fill in the template 
    lammps_script = 'in.diffusion.in'
    with open("in.diffusion_msd.template",'r') as template_f:
        with open(lammps_script,'w') as f:
            f.write(filltemplate(template_f,lammps_variables,'<','>'))
    
    # Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile='diffusion_msd.log.lammps')
    
    results = {}

    thermo_index = 0
    if eq_Equibilibrium:
        thermo_index += 1


    log = lmp.Log('diffusion_msd.log.lammps')
    runningDiffusion = log.simulations[thermo_index].thermo['v_fitslope']
    runningTemperature = log.simulations[thermo_index].thermo['Temp']
    runningMSD = log.simulations[thermo_index].thermo['c_msd[4]']
    Diffusion_coeff = np.average(runningDiffusion[Data_step:])
    print(len(runningDiffusion))
    AveTemp = np.average(runningTemperature[Data_step:])
    AveMSD = np.average(runningMSD[Data_step:])
    #unit conversions 
    unitString1 = f"({lamps_units['length']}^2)/({lamps_units['time']})"
    print(unitString1)
    unitString2 = f"({lamps_units['length']}^2)"
    D = uc.set_in_units(Diffusion_coeff,unitString1)
    
    MSD = uc.set_in_units(AveMSD,unitString2)

    results['diffusion'] = D
    results['mean_sqaured_displacement'] = MSD
    results['temperature'] = AveTemp
    print(uc.get_in_units(D,'cm^2/s'))
    return results
    

    