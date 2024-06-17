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
              potential: lmp.Potential,
              system: am.System,
              mpi_command: Optional[str] = None,
              temperature: float = 200,
              timestep: float = .5,
              correlationlength: int = 400,
              sampleinterval: int = 5,
              outputsteps: int = 2000,
              runsteps: int = 100000,
              dataoffset: int = 500,
              eq_thermosteps: int = 0,
              eq_runsteps: int = 0,
              eq_equilibrium: bool = False,
              dragcoeff: float = .2,
              randomseed: int = 543212
              ) -> dict:
    
    #Get the Units from Potential
    lamps_units = lmp.style.unit(potential.units)

    #Initialize the variables to fill in the script
    lammps_variables = {}

    #Get the system info by loading the system into the init.dat and using the specified potential
    system_info = system.dump('atom_data',f='init.dat',potential = potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    kb_SI = uc.set_in_units(1.3806504*(10**(-23)),"(kg*m^2)/(s^2*K)")

    mass_unit = lamps_units['mass']
    if mass_unit == "g/mol": mass_unit = 'g'

    unitStringKB = f"({mass_unit}*{lamps_units['length']}^2)/({lamps_units['time']}^2*{lamps_units['temperature']})"
    kb = uc.get_in_units(kb_SI,unitStringKB)
    print(f"kb={kb}",unitStringKB)
    print(f"{uc.get_in_units(kb_SI,'(kg*m^2)/(s^2*K)')} - in J/K")


    unitStringScale = f"({mass_unit})/({lamps_units['length']}*{lamps_units['time']}^2)"
    scale_unit = uc.set_in_units(1,f"{lamps_units['pressure']}")
    scale = uc.get_in_units(scale_unit,unitStringScale)
    print(scale,unitStringScale)


    #Initialize the rest of the inputs to the Lammps Scripts 
    lammps_variables['Temperature'] = temperature
    lammps_variables['Time_Step'] = timestep
    lammps_variables['Correlation_Length'] = correlationlength
    lammps_variables['Sample_Interval'] = sampleinterval
    lammps_variables['Run_length'] = runsteps
    lammps_variables['Dump_Interval'] = outputsteps
    #Weird conversion tools 
    lammps_variables['Boltzman_constant'] = kb
    lammps_variables['Scale'] = scale 
    lammps_variables['Drag_coeff'] = dragcoeff 

    #Setting up equibilrium run 
    if eq_equilibrium:
        instruct = f"""fix NVE all nve \n fix LANGEVIN all langevin $T $T {10*timestep} {randomseed} \n
                        thermo {eq_thermosteps} \n run {eq_runsteps} \n unfix NVE \n unfix LANGEVIN \n
                        reset_timestep 0"""
        lammps_variables['Equilibration_instructions'] = instruct
    elif not eq_equilibrium or eq_runsteps == 0:
        lammps_variables['Equilibration_instructions'] = ""


    #Fill in the template 
    lammps_script = 'in.viscosity.in'
    template = read_calc_file('iprPy.calculation.viscosity_green_kubo',
                              'in.viscosity_green_kubo.template')
    #with open("in.diffusion_msd.template",'r') as template_f:
    with open(lammps_script,'w') as f:
        f.write(filltemplate(template,lammps_variables,'<','>'))
    
    #Run lamps
    output = lmp.run(lammps_command,script_name=lammps_script,
                     mpi_command=mpi_command,screen=False,logfile="viscosity.log.lammps")
    
    log = lmp.Log('viscosity.log.lammps')

    thermo_index = 0
    if eq_equilibrium:
        thermo_index += 1

    #From thermo data calculate the Viscosity 
    log = lmp.Log('viscosity.log.lammps')
    runningViscosity = log.simulations[thermo_index].thermo["v_v"]
    runningTemperature = log.simulations[thermo_index].thermo["Temp"]

    running_pxy = log.simulations[thermo_index].thermo['v_pxy']
    running_pxz = log.simulations[thermo_index].thermo['v_pxz']
    running_pyz = log.simulations[thermo_index].thermo['v_pyz']

    running_vx = log.simulations[thermo_index].thermo['v_v11']
    running_vy = log.simulations[thermo_index].thermo['v_v22']
    running_vz = log.simulations[thermo_index].thermo['v_v33']

    Viscosity = np.average(runningViscosity[dataoffset:])
    AveTemp = np.average(runningTemperature[dataoffset:])


    #Initialize the return dictionary
    results = {}
    #Data of interest
    results['viscosity_stderr'] = np.std(runningViscosity[dataoffset:])
    results['viscosity'] = Viscosity
    results['measured_temperature'] = AveTemp
    results['measured_temperature_stderr'] = np.std(runningTemperature[dataoffset:])

    results['pxy_values'] = running_pxy[dataoffset:]
    results['pxz_values'] = running_pxz[dataoffset:]
    results['pyz_values'] = running_pyz[dataoffset:]

    results['vx_value'] = np.average(running_vx[dataoffset:])
    results['vy_value'] = np.average(running_vy[dataoffset:])
    results['vz_value'] = np.average(running_vz[dataoffset:])

    results['lammps_output'] = output
    return results