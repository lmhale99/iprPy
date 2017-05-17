#!/usr/bin/env python

#Python script created by Lucas Hale

#Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
from copy import deepcopy
import glob

#http://www.numpy.org/
import numpy as np 

#https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

#https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):    
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])

    interpret_input(input_dict)  
    
    #Run pointdiffusion 
    results_dict = pointdiffusion(input_dict['lammps_command'], 
                                  input_dict['initialsystem'], 
                                  input_dict['potential'], 
                                  input_dict['symbols'],
                                  input_dict['pointdefect_model'],
                                  mpi_command = input_dict['mpi_command'],
                                  temperature = input_dict['temperature'],
                                  runsteps =    input_dict['runsteps'],
                                  thermosteps = input_dict['thermosteps'],
                                  dumpsteps =   input_dict['dumpsteps'],
                                  equilsteps =  input_dict['equilsteps'],
                                  randomseed =  input_dict['randomseed'])
                                  
    #Save data model of results 
    results = data_model(input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
        
def pointdiffusion(lammps_command, system, potential, symbols, ptd_model,
                   mpi_command=None, temperature=300,
                   runsteps=100000, thermosteps=None, dumpsteps=None, 
                   equilsteps=20000, randomseed=None):
                   
    """
    Evaluates the diffusion rate of a point defect at a given temperature. This
    method will run two simulations: an NVT run at the specified temperature to 
    equilibrate the system, then an NVE run to measure the defect's diffusion 
    rate. The diffusion rate is evaluated using the mean squared displacement of
    all atoms in the system, and using the assumption that diffusion is only due
    to the added defect(s).
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to dynamically relax
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    ptd_model -- DataModelDict representation of a point defect data model.
    
    Keyword Arguments:
    temperature -- temperature to relax at. Default value is 300.
    runsteps -- number of NVE integration steps to perform. Default value is 100000. 
    thermosteps -- output thermo values every this many steps. Default value is 
                    runsteps/1000.
    dumpsteps -- output dump files every this many steps. Default value is runsteps
                  (only first and last steps are outputted as dump files).
    equilsteps -- number of NVT integration steps to perform to equilibriate the system. Default value is 20000.
    randomseed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
    """
    
    #Add defect(s) to the initially perfect system
    for params in ptd_model.iterfinds('atomman-defect-point-parameters'):       
        system = am.defect.point(system, **params)
        
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Check that temperature is greater than zero
    if temperature <= 0.0:
        raise ValueError('Temperature must be greater than zero')
    
    #Handle default values
    if thermosteps is None: 
        if thermosteps >= 1000:
            thermosteps = runsteps/1000
        else:
            thermosteps = 1
    
    if dumpsteps is None:
        dumpsteps = runsteps
        
    if randomseed is None:
        randomseed = random.randint(1, 900000000)
    
    
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'initial.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['temperature'] = temperature
    lammps_variables['runsteps'] = runsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['randomseed'] = randomseed
    lammps_variables['timestep'] = lmp.style.timestep(potential.units)
    
    #Write lammps input script
    template_file = 'diffusion.template'
    lammps_script = 'diffusion.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    #run lammps to relax perfect.dat
    output = lmp.run(lammps_command, 'diffusion.in', mpi_command)
    
    #Extract LAMMPS thermo data.
    












































    
    
        