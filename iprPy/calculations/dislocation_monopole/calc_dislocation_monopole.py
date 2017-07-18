#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import glob
import shutil
import random
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calc_style and record_style
calc_style = 'dislocation_monopole'
record_style = 'calculation-dislocation-monopole'

def main(*args):
    """Main function for running calculation"""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
   
    results_dict = dislocationmonopole(input_dict['lammps_command'], 
                                       input_dict['initialsystem'], 
                                       input_dict['potential'], 
                                       input_dict['symbols'], 
                                       input_dict['burgersvector'], 
                                       input_dict['C'], 
                                       axes =        input_dict['axes'],
                                       mpi_command = input_dict['mpi_command'], 
                                       etol =        input_dict['energytolerance'], 
                                       ftol =        input_dict['forcetolerance'], 
                                       maxiter =     input_dict['maxiterations'], 
                                       maxeval =     input_dict['maxevaluations'], 
                                       dmax =        input_dict['maxatommotion'],
                                       annealtemp =  input_dict['annealtemperature'], 
                                       randomseed =  input_dict['randomseed'], 
                                       bwidth =      input_dict['boundarywidth'], 
                                       bshape =      input_dict['dislocation_boundaryshape'])
    
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def dislocationmonopole(lammps_command, system, potential, symbols, burgers, C, 
                         mpi_command=None, axes=None, randomseed=None,
                         etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
                         annealtemp=0.0, bwidth=uc.set_in_units(10, 'angstrom'), bshape='circle'):    
    # Initialize results dict
    results_dict = {}    
    
    # Save initial perfect system
    am.lammps.atom_dump.dump(system, 'base.dump')
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = symbols

    # Solve Stroh method for dislocation
    stroh = am.defect.Stroh(C, burgers, axes=axes)
    results_dict['Stroh_preln'] = stroh.preln
    results_dict['Stroh_K_tensor'] = stroh.K_tensor    
    
    # Generate dislocation system by displacing atoms according to Stroh solution
    disp = stroh.displacement(system.atoms.view['pos'])
    system.atoms.view['pos'] += disp

    system.wrap()
    
    # Apply fixed boundary conditions
    system, symbols = disl_boundary_fix(system, symbols, bwidth, bshape)
    
    # Relax system
    relaxed = disl_relax(lammps_command, system, potential, symbols, 
                         mpi_command = mpi_command, 
                         annealtemp = annealtemp,
                         etol = etol, 
                         ftol = ftol, 
                         maxiter = maxiter, 
                         maxeval = maxeval)
    
    # Save relaxed dislocation system with original box vects
    system_disl = am.load('atom_dump', relaxed['dumpfile'])[0]

    system_disl.box_set(vects=system.box.vects, origin=system.box.origin)
    lmp.atom_dump.dump(system_disl, 'disl.dump')
    results_dict['dumpfile_disl'] = 'disl.dump'
    results_dict['symbols_disl'] = symbols
    
    results_dict['E_total_disl'] = relaxed['E_total']
    
    # Cleanup atom.* files
    for atomfile in glob.iglob('*.dump'):
        os.remove(atomfile)
    
    return results_dict

def disl_boundary_fix(system, symbols, bwidth, bshape='circle'):
    """Create boundary region by changing atom types. Returns a new system and symbols list."""
    natypes = system.natypes
    atypes = system.atoms_prop(key='atype')
    pos = system.atoms_prop(key='pos')
    
    if bshape == 'circle':
        # Find x or y bound closest to 0
        smallest_xy = min([abs(system.box.xlo), abs(system.box.xhi),
                           abs(system.box.ylo), abs(system.box.yhi)])
        
        radius = smallest_xy - bwidth
        xy_mag = np.linalg.norm(system.atoms_prop(key='pos')[:,:2], axis=1)        
        atypes[xy_mag > radius] += natypes
    
    elif bshape == 'rect':
        index = np.unique(np.hstack((np.where(pos[:,0] < system.box.xlo + bwidth),
                                     np.where(pos[:,0] > system.box.xhi - bwidth),
                                     np.where(pos[:,1] < system.box.ylo + bwidth),
                                     np.where(pos[:,1] > system.box.yhi - bwidth))))
        atypes[index] += natypes
           
    else:
        raise ValueError("Unknown boundary shape type! Enter 'circle' or 'rect'")

    new_system = deepcopy(system)
    new_system.atoms_prop(key='atype', value=atypes)
    symbols.extend(symbols)
    
    return new_system, symbols
        
def disl_relax(lammps_command, system, potential, symbols, 
               mpi_command=None, annealtemp=0.0, randomseed=None,
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000, dmax=0.01):
    """Runs LAMMPS using the disl_relax.in script for relaxing a dislocation monopole system."""
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = iprPy.tools.check_lammps_version(lammps_command)['lammps_date']
    
    # Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'system.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['anneal_info'] =         anneal_info(annealtemp, randomseed, potential.units)
    lammps_variables['etol'] =    etol
    lammps_variables['ftol'] =     uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] =  maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    lammps_variables['group_move'] =          ' '.join(np.array(range(1, system.natypes//2+1), dtype=str))
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = 'disl_relax.template'
    lammps_script = 'disl_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))    

    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object')
    thermo = output.simulations[-1]['thermo']
    
    # Extract output values
    results = {}
    results['logfile'] = 'log.lammps'
    results['dumpfile'] = '%i.dump' % thermo.Step.values[-1] 
    results['E_total'] = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    
    return results

def anneal_info(temperature=0.0, randomseed=None, units='metal'):
    """
    Generates LAMMPS commands for thermo anneal. 
    
    Keyword Arguments:
    temperature -- temperature to relax at. Default value is 0. 
    randomseed -- random number seed used by LAMMPS for velocity creation. 
                  Default value generates a new random integer every time.
    units -- LAMMPS units style to use.
    """
    # Get lammps units
    lammps_units = lmp.style.unit(units)
    
    # Return nothing if temperature is 0.0 (don't do thermo anneal)
    if temperature == 0.0:
        return ''
    
    # Generate velocity, fix nvt, and run LAMMPS command lines
    else:
        if randomseed is None: 
            randomseed = random.randint(1, 900000000)
            
        start_temp = 2 * temperature
        tdamp = 100 * lmp.style.timestep(units)
        timestep = lmp.style.timestep(units)
        info = '\n'.join(['velocity move create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
                           'fix nvt all nvt temp %f %f %f' % (temperature, temperature, tdamp),
                           'timestep %f' % (timestep),
                           'thermo 10000',
                           'run 10000'])

    return info
    
def process_input(input_dict, UUID=None, build=True):
    """Reads the calc_*.in input commands for this calculation and sets default values if needed."""
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '-10 10 -10 10 0 3')
    input_dict['boundaryshape'] =  input_dict.get('dislocation_boundaryshape', 'circle')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
    input_dict['randomseed'] =     int(input_dict.get('randomseed',  
                                       random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['energytolerance'] =   float(input_dict.get('energytolerance', 0.0))
    input_dict['annealtemperature'] = float(input_dict.get('annealtemperature', 0.0))
    input_dict['boundarywidth'] =     float(input_dict.get('dislocation_boundarywidth', 3.0))
    
    # These are calculation-specific default floats with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-6 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Load dislocation parameters
    iprPy.input.dislocationmonopole(input_dict)
    
    # Load elastic constants
    iprPy.input.elasticconstants(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
        


if __name__ == '__main__':
    main(*sys.argv[1:])    