#!/usr/bin/env python

#Python script created by Lucas Hale and Norman Luu.

#Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
from copy import deepcopy

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

calc_name = os.path.splitext(os.path.basename(__file__))[0]
assert calc_name[:5] == 'calc_', 'Calculation file name must start with "calc_"'
calc_type = calc_name[5:]

def main(*args):
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])
    
    interpret_input(input_dict)
   
    results_dict = surface_energy(input_dict['lammps_command'], 
                                  input_dict['initialsystem'], 
                                  input_dict['potential'], 
                                  input_dict['symbols'], 
                                  mpi_command = input_dict['mpi_command'], 
                                  etol =        input_dict['energytolerance'], 
                                  ftol =        input_dict['forcetolerance'], 
                                  maxiter =     input_dict['maxiterations'], 
                                  maxeval =     input_dict['maxevaluations'], 
                                  dmax =        input_dict['maxatommotion'],
                                  cutboxvector = input_dict['surface_cutboxvector'])
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def surface_energy(lammps_command, system, potential, symbols, mpi_command=None, 
                   etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01,
                   cutboxvector='c'):
    """
    This calculates surface energies by comparing the energy of a system with 
    all periodic boundaries to the same system with one non-periodic boundary,
    effectively cutting along that atomic plane.
    """
      
    #Initialize results dictionary
    results_dict = {}
    
    #Evaluate perfect system
    system.pbc = [True, True, True]
    perfect = relax_system(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                           etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
    #Extract results from perfect system
    shutil.move(perfect['finaldumpfile'], 'perfect.dump')
    shutil.move('log.lammps', 'perfect-log.lammps')
    results_dict['perfect_system_file'] = 'perfect.dump'
    results_dict['Ecoh'] = perfect['potentialenergy'] / system.natoms    

    #Set up defect system
    #surfacearea is area of parallelogram defined by the two box vectors not along the cutboxvector
    if   cutboxvector == 'a':
        system.pbc[0] = False
        surfacearea = 2 * np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
        
    elif cutboxvector == 'b':
        system.pbc[1] = False
        surfacearea = 2 * np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
        
    elif cutboxvector == 'c':
        system.pbc[2] = False
        surfacearea = 2 * np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
        
    else:
        raise ValueError('Invalid cutboxvector')
        
    #Evaluate system with free surface
    surface = relax_system(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                          etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
    #Extract results from system with free surface
    shutil.move(surface['finaldumpfile'], 'surface.dump')
    shutil.move('log.lammps', 'surface-log.lammps')
    results_dict['surface_system_file'] = 'perfect.dump'
    results_dict['surface_energy'] = (surface['potentialenergy'] - perfect['potentialenergy']) / surfacearea
    results_dict['surfacearea'] = surfacearea
    return results_dict    
    
def relax_system(lammps_command, system, potential, symbols, mpi_command=None, 
                 etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01):
    """
    Sets up and runs the min LAMMPS script for statically relaxing a system
    """

    #Ensure all atoms are within the system's box
    system.wrap()
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
   
    #Define lammps variables
    lammps_variables = {}
    
    #Generate system and pair info
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'system.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    
    #Pass in run parameters
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    #Set dump_modify format based on dump_modify_version
    dump_modify_version = iprPy.tools.lammps_version.dump_modify(lammps_command)
    if dump_modify_version == 0:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    elif dump_modify_version == 1:
        lammps_variables['dump_modify_format'] = '"%i %i %.13e %.13e %.13e %.13e"'    
    
    #Write lammps input script
    template_file = 'min.template'
    lammps_script = 'min.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    #run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object')
    
    #Extract output values
    results = {}
    results['logfile'] =         'log.lammps'
    results['initialdatafile'] = 'system.dat'
    results['initialdumpfile'] = 'atom.0'
    results['finaldumpfile'] =   'atom.%i' % output.simulations[-1]['thermo'].Step.tolist()[-1] 
    results['potentialenergy'] = uc.set_in_units(output.simulations[-1]['thermo'].PotEng.tolist()[-1], lammps_units['energy'])
    
    return results
    
def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    #set calculation UUID
    if UUID is not None: input_dict['calc_key'] = UUID
    else: input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    #Verify required terms are defined
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    assert 'potential_file' in input_dict, 'potential_file value not supplied'
    assert 'load'           in input_dict, 'load value not supplied'
    
    #Assign default values to undefined terms
    iprPy.input.units(input_dict)
    
    input_dict['mpi_command'] =    input_dict.get('mpi_command',    None)
    input_dict['potential_dir'] =  input_dict.get('potential_dir',  '')
    
    input_dict['load_options'] =   input_dict.get('load_options',   None)
    input_dict['box_parameters'] = input_dict.get('box_parameters', None)
    input_dict['symbols'] =        input_dict.get('symbols',        None)
       
    input_dict['sizemults'] =      input_dict.get('sizemults',     '3 3 3')
    iprPy.input.sizemults(input_dict)
    
    #these are integer terms
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
        
    #these are unitless float terms
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    
    #these are terms with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-6 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    #Check if surface_model was defined
    if 'surface_model' in input_dict:
        #Verify competing parameters are not defined
        assert 'atomshift'            not in input_dict, 'atomshift and surface_model cannot both be supplied'
        assert 'x_axis'               not in input_dict, 'x_axis and surface_model cannot both be supplied'
        assert 'y_axis'               not in input_dict, 'y_axis and surface_model cannot both be supplied'
        assert 'z_axis'               not in input_dict, 'z_axis and surface_model cannot both be supplied'
        assert 'surface_cutboxvector' not in input_dict, 'surface_cutboxvector and surface_model cannot both be supplied'
    else:
        input_dict['surface_model'] = None
        input_dict['surface_cutboxvector'] = input_dict.get('surface_cutboxvector', 'c')
        assert input_dict['surface_cutboxvector'] in ['a', 'b', 'c'], 'invalid surface_cutboxvector'
    
    return input_dict

def interpret_surface_model(input_dict):
    """Read/handle parameters associated with the surface model (axes, cutboxvector, and atomshift)"""
    
    #Check if surface_model was defined
    if input_dict['surface_model'] is not None:
        
        #Load surface_model
        try:
            with open(input_dict['surface_model']) as f:
                input_dict['surface_model'] = DM(f).find('free-surface')
        except:
            raise ValueError('Invalid surface_model')
            
        #Extract parameter values from surface_model        
        params = input_dict['surface_model']['atomman-surface-parameters']
        input_dict['x_axis'] = params['crystallographic-axes']['x-axis']
        input_dict['y_axis'] = params['crystallographic-axes']['y-axis']
        input_dict['z_axis'] = params['crystallographic-axes']['z-axis']
        input_dict['surface_cutboxvector'] = params['cutboxvector']
        input_dict['atomshift'] = params['atomshift']
    
    #If surface_model is not defined
    else:
        iprPy.input.axes(input_dict)
        iprPy.input.atomshift(input_dict)
        
def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
    
    interpret_surface_model(input_dict)
    
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)
    
def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-surface-energy'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = calc_name
    
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['load_options'] = input_dict['load_options']
    
    run_params['energytolerance']    = input_dict['energytolerance']
    run_params['forcetolerance']     = input_dict['forcetolerance']
    run_params['maxiterations']  = input_dict['maxiterations']
    run_params['maxevaluations'] = input_dict['maxevaluations']
    run_params['maxatommotion']      = input_dict['maxatommotion']
    
    #Copy over potential data model info
    calc['potential'] = DM()
    calc['potential']['key'] = input_dict['potential'].key
    calc['potential']['id'] = input_dict['potential'].id
    
    #Save info on system file loaded
    system_load = input_dict['load'].split(' ')    
    calc['system-info'] = DM()
    calc['system-info']['artifact'] = DM()
    calc['system-info']['artifact']['file'] = os.path.basename(' '.join(system_load[1:]))
    calc['system-info']['artifact']['format'] = system_load[0]
    calc['system-info']['artifact']['family'] = input_dict['system_family']
    calc['system-info']['symbols'] = input_dict['symbols']
    
    #Save defect parameters
    calc['free-surface'] = surf = DM()
    if input_dict['surface_model'] is not None:
        surf['key'] = input_dict['surface_model']['key']
        surf['id'] =  input_dict['surface_model']['id']
    
    surf['system-family'] = input_dict['system_family']
    surf['atomman-surface-parameters'] = asp = DM()    
    asp['crystallographic-axes'] = DM()
    asp['crystallographic-axes']['x-axis'] = input_dict['x_axis']
    asp['crystallographic-axes']['y-axis'] = input_dict['y_axis']
    asp['crystallographic-axes']['z-axis'] = input_dict['z_axis']
    asp['cutboxvector'] = input_dict['surface_cutboxvector']
    asp['atomshift'] = input_dict['atomshift']
        
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:        
        #Save the cohesive energy
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['Ecoh'], 
                                                                input_dict['energy_unit'])), 
                                      ('unit', input_dict['energy_unit'])])
        
        #Save the free surface energy
        calc['free-surface-energy'] = DM([('value', uc.get_in_units(results_dict['surface_energy'], 
                                                                    input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')), 
                                          ('unit', input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')])

    return output
        
if __name__ == '__main__':
    main(*sys.argv[1:])     
    
