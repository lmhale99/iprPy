#current in 6/11/24 - duplicated in working directoy

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

def calculate_diffusion_vacf(lammps_command:str,
              potential: lmp.Potential,
              system: am.System,
              mpi_command: Optional[str] = None,
              temperature: float = 300,
              timestep: float = .5,
              run_steps: int = 10000,
              Equilibration_Thermo_steps: int = 100,
              Equilibration_Run_steps: int = 1000,
              Simulation_runs: int = 5,
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
    lammps_variables['Run_length'] = run_steps
    lammps_variables['Equilibration_thermo'] = Equilibration_Thermo_steps
    lammps_variables['Equilibration_steps'] = Equilibration_Run_steps
    lammps_variables['num_simulations'] = Simulation_runs
    lammps_variables['Degrees_freedom'] = Degrees_freedom
    #Fill in the template 

    #Setting up equilbrium
    if eq_Equibilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} 498094 \n
                        thermo {eq_Thermo_steps} \n run {eq_Run_steps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_Equibilibrium or eq_Run_steps == 0:
        lammps_variables['Equilibration_instructions'] = ""


    lammps_script = 'in.diffusion.in'
    with open("in.diffusion_vacf.template",'r') as template_f:
        with open(lammps_script,'w') as f:
            f.write(filltemplate(template_f,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="diffusion_vacf.log.lammps")
    
    results = {}

    indexOffset = 0
    if eq_Equibilibrium: 
        indexOffset += 1

    log = lmp.Log('diffusion_vacf.log.lammps')
    D = np.ndarray((Simulation_runs,run_steps+1))
    T = np.ndarray((Simulation_runs,run_steps+1))
    for i in range(indexOffset,Simulation_runs+indexOffset):
        D[i-indexOffset] = log.simulations[i].thermo['v_vacf']
        T[i-indexOffset] = log.simulations[i].thermo['Temp']
    runningDiffusion = np.average(D,axis=1)
    runningTemperature = np.average(D,axis=1)

    Diffusion_coeff = np.average(runningDiffusion)
    AveTemp = np.average(runningTemperature)
    
    #unit conversions 
    unitString1 = f"({lamps_units['length']}^2)/({lamps_units['time']})"
    Diff_coeff = uc.set_in_units(Diffusion_coeff,unitString1)
    results['diffusion'] = Diff_coeff
    results['temperature'] = AveTemp
    print(uc.get_in_units(Diff_coeff,'cm^2/s'))
    return results
    

    