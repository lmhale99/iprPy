#current in 6/11/24 - duplicated in working directoy

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

def diffusion_vacf(lammps_command:str,
              potential: lmp.Potential,
              system: am.System,
              mpi_command: Optional[str] = None,
              randomseed: Optional[int] = None,
              temperature: float = 300,
              timestep: float = .5,
              runsteps: int = 10000,
              simruns: int = 5,
              dumpsteps: int = 0,
              directoryname: Optional[str] = None,
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
    lammps_variables['Equilibration_thermo'] = eq_thermosteps
    lammps_variables['Equilibration_steps'] = eq_runsteps
    lammps_variables['num_simulations'] = simruns
    lammps_variables['Degrees_freedom'] = degrees_freedom
    #Fill in the template 

    if randomseed is None:
        randomseed = random.randint(1,9000000)

    if (dumpsteps != 0) or (dumpsteps != None):
        mkdir(directoryname,simruns)
        instruct = f"dump            dumpy all custom {dumpsteps} {directoryname}/$i/*.dump id type x y z"
        lammps_variables['Dump_instructions'] = instruct 
        lammps_variables['Dump_unfix'] = "undump dumpy"
    else: 
        lammps_variables['Dump_instructions'] = ""
        lammps_variables['Dump_unfix'] = ""

    #Setting up equilbrium
    if eq_equilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} {randomseed} \n
                        thermo {eq_thermosteps} \n run {eq_runsteps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_equilibrium or eq_runsteps == 0:
        lammps_variables['Equilibration_instructions'] = ""


    lammps_script = 'in.diffusion.in'
    template = read_calc_file('iprPy.calculation.diffusion_vacf',
                              'in.diffusion_vacf.template')

    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="diffusion_vacf.log.lammps")
    
    results = {}

    indexOffset = 0
    if eq_equilibrium: 
        indexOffset += 1

    log = lmp.Log('diffusion_vacf.log.lammps')
    D = np.ndarray((simruns,runsteps+1))
    T = np.ndarray((simruns,runsteps+1))
    v1 = np.ndarray((simruns,runsteps+1))
    v2 = np.ndarray((simruns,runsteps+1))
    v3 = np.ndarray((simruns,runsteps+1))
    v = np.ndarray((simruns,runsteps+1))
    for i in range(indexOffset,simruns+indexOffset):
        D[i-indexOffset] = log.simulations[i].thermo['v_eta'] #This is the integrated value - dumb name
        T[i-indexOffset] = log.simulations[i].thermo['Temp']
        v1[i-indexOffset] = log.simulations[i].thermo['c_vacf[1]']
        v2[i-indexOffset] = log.simulations[i].thermo['c_vacf[2]']
        v3[i-indexOffset] = log.simulations[i].thermo['c_vacf[3]']
        v[i-indexOffset] = log.simulations[i].thermo['c_vacf[4]']

    runningDiffusion = np.average(D,axis=1)
    runningTemperature = np.average(D,axis=1)
    runningv1 = np.average(v1,axis=1)
    runningv2 = np.average(v2,axis=1)
    runningv3 = np.average(v3,axis=1)
    runningv = np.average(v,axis=1)

    Diffusion_coeff = np.average(runningDiffusion)
    Diffusion_coeff_err = np.std(runningDiffusion)
    AveTemp = np.average(runningTemperature)
    AveTemp_err = np.std(runningTemperature)
    
    #unit conversions 
    # unitString1 = f"({lamps_units['length']}^2)/({lamps_units['time']})"




    results['vacf_x_values'] = runningv1
    results['vacf_y_values'] = runningv2
    results['vacf_z_values'] = runningv3
    results['vacf_values'] = runningv
    results['diffusion'] = Diffusion_coeff
    results['diffusion_stderr'] = Diffusion_coeff_err
    results['measured_temperature'] = AveTemp
    results['measured_temperature_stderr'] = AveTemp_err
    results['lammps_output'] = output 
    return results
    

import os 
def mkdir(name,runs):
    os.mkdir(name)
    for i in range(1,runs+1):
        path = os.path.join(name,str(i))
        try:
            os.mkdir(path)
        except:
            print("Directory Already Exists - Please use a different name")
    