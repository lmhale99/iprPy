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
              directoryname: Optional[str] = None,
              dataoffset: int = 500,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              dumpsteps: int = 0,
              randomseed: Optional[int] = None,
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
    lammps_variables['runsteps'] = runsteps
    lammps_variables['drivingforce'] = drivingforce
    lammps_variables['thermosteps'] = thermosteps

    #Setting up dump instructions
    if (dumpsteps != 0) and (dumpsteps != None):
        if not Path(directoryname).exists():
            Path(directoryname).mkdir(parents=True)
        instruct = f"""dump         dumpy all custom {dumpsteps} {directoryname}/*.dump id type x y z"""
        lammps_variables["Dump_instructions"] = instruct
    else:
        lammps_variables['Dump_instructions'] = ""

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
    runningViscosityInverse = thermo["v_reciprocalViscosity"]
    runningTemperature = thermo["Temp"]
    runningViscosity = np.array([1/i for i in runningViscosityInverse])
    Viscosity = np.average(runningViscosity[dataoffset:])
    AveTemp = np.average(runningTemperature[dataoffset:])
    #Unit Conversions
    unitString = f"({lammps_units['length']}^3*{lammps_units['density']})/({lammps_units['velocity']}*{lammps_units['time']}^2)"
    #error propogation formula sigma_eta = sigma_inverse_visc / visc^2
    eta_std_val = np.std(runningViscosityInverse)/(Viscosity**2)
    #Initialize the return dictionary
    results = {}

    #Data of interest
    results['viscosity'] = uc.set_in_units(Viscosity,unitString)
    results['viscosity_stderr'] = uc.set_in_units(eta_std_val,unitString)
    results['measured_temperature'] = uc.set_in_units(AveTemp,'K')
    results['measured_temperature_stderr'] = uc.set_in_units(np.std(runningTemperature[dataoffset:]),'K')
    results['lammps_output'] = output    
    return results
 

