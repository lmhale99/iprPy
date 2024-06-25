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

def diffusion_vacf(lammps_command:str,
              system: am.System,
              potential: lmp.Potential,
              temperature: float,
              mpi_command: Optional[str] = None,
              timestep: Optional[float] = None,
              dumpsteps: int = 0,
              runsteps: int = 10000,
              simruns: int = 5,
              degrees_freedom: int = 3,
              directoryname: Optional[str] = None,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              randomseed: Optional[int] = None
              ) -> dict:
    
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
    lammps_variables['Time_Step'] = timestep
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Equilibration_thermo'] = eq_thermosteps
    lammps_variables['Equilibration_steps'] = eq_runsteps
    lammps_variables['num_simulations'] = simruns
    lammps_variables['Degrees_freedom'] = degrees_freedom

    #Setting up dump instrcutions
    if (dumpsteps != 0) and (dumpsteps != None):
        if not Path(directoryname).exists():
            Path(directoryname).mkdir(parents=True)
        instruct = f"dump            dumpy all custom {dumpsteps} {directoryname}/$i/*.dump id type x y z"
        lammps_variables['Dump_instructions'] = instruct 
        lammps_variables['Dump_unfix'] = "undump dumpy"
    else: 
        lammps_variables['Dump_instructions'] = ""
        lammps_variables['Dump_unfix'] = ""

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
        D[i-indexOffset] = log.simulations[i].thermo['v_eta'] 
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

    diffusionUnitString = f'{lammps_units['velocity']}^2*{lammps_units['time']}'
    vacfUnitString = f'{lammps_units['velocity']}^2'

    results['vacf_x_values'] = uc.set_in_units(runningv1,vacfUnitString)
    results['vacf_y_values'] = uc.set_in_units(runningv2,vacfUnitString)
    results['vacf_z_values'] = uc.set_in_units(runningv3,vacfUnitString)
    results['vacf_values'] = uc.set_in_units(runningv,vacfUnitString)
    results['diffusion'] = uc.set_in_units(Diffusion_coeff,diffusionUnitString)
    results['diffusion_stderr'] = uc.set_in_units(Diffusion_coeff_err,diffusionUnitString)
    results['measured_temperature'] = uc.set_in_units(AveTemp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(AveTemp_err,'K')
    results['lammps_output'] = output 
    return results
    
    