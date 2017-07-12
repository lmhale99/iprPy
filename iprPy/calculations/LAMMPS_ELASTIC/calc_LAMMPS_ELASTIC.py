#!/usr/bin/env python

# Python script created by Lucas Hale
# Built around LAMMPS script by Steve Plimpton

# Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import glob
import shutil
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
calc_style = 'LAMMPS_ELASTIC'
record_style = 'calculation-system-relax'

def main(*args):
    """Main function for running calculation"""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
    
    if input_dict['convergevalues'] is True:
        # Run lammps_ELASTIC_refine to refine values
        results_dict = lammps_ELASTIC_refine(input_dict['lammps_command'], 
                                             input_dict['initialsystem'],
                                             input_dict['potential'],
                                             input_dict['symbols'],
                                             mpi_command =   input_dict['mpi_command'],
                                             ucell =         input_dict['ucell'],
                                             strainrange =   input_dict['strainrange'],
                                             etol =          input_dict['energytolerance'],
                                             ftol =          input_dict['forcetolerance'],
                                             maxiter =       input_dict['maxiterations'],
                                             maxeval =       input_dict['maxevaluations'],
                                             dmax =          input_dict['maxatommotion'],
                                             pressure_unit = input_dict['pressure_unit'])
    else:
        # Run lammps_ELASTIC to refine values
        results_dict = lammps_ELASTIC(       input_dict['lammps_command'], 
                                             input_dict['initialsystem'],
                                             input_dict['potential'],
                                             input_dict['symbols'],
                                             mpi_command =   input_dict['mpi_command'],
                                             ucell =         input_dict['ucell'],
                                             strainrange =   input_dict['strainrange'],
                                             etol =          input_dict['energytolerance'],
                                             ftol =          input_dict['forcetolerance'],
                                             maxiter =       input_dict['maxiterations'],
                                             maxeval =       input_dict['maxevaluations'],
                                             dmax =          input_dict['maxatommotion'],
                                             pressure_unit = input_dict['pressure_unit'])
                                  
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def lammps_ELASTIC_refine(lammps_command, system, potential, symbols, 
                          mpi_command=None, ucell=None,
                          strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, 
                          dmax=uc.set_in_units(0.01, 'angstrom'), pressure_unit='GPa', tol=1e-10):
    """Repeatedly runs the ELASTIC example distributed with LAMMPS until box dimensions converge"""
    
    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_b = system.box.b / ucell.box.b
    lz_c = system.box.c / ucell.box.c
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma    
    
    old_results = lammps_ELASTIC(lammps_command, system, potential, symbols, 
                                 mpi_command=mpi_command, ucell=None,
                                 strainrange=strainrange, etol=etol, ftol=ftol, 
                                 maxiter=maxiter, maxeval=maxeval, 
                                 dmax=dmax, pressure_unit=pressure_unit)
    shutil.move('log.lammps', 'elastic-0-log.lammps')
    os.remove('atom.0')
    for atom_dump in glob.iglob('atom.*'):
        shutil.move(atom_dump, 'elastic-0-config.dump') 
    
    converged = False
    for cycle in xrange(1, 100):
        new_results = lammps_ELASTIC(lammps_command, old_results['system_relaxed'], potential, symbols, 
                                     mpi_command=mpi_command, ucell=None,
                                     strainrange=strainrange, etol=etol, ftol=ftol, 
                                     maxiter=maxiter, maxeval=maxeval, 
                                     dmax=dmax, pressure_unit=pressure_unit)
        shutil.move('log.lammps', 'elastic-'+str(cycle)+'-log.lammps')
        os.remove('atom.0')
        for atom_dump in glob.iglob('atom.*'):
            shutil.move(atom_dump, 'elastic-'+str(cycle)+'-config.dump')
        
        # Test if box dimensions have converged
        if (np.isclose(old_results['a_lat'], new_results['a_lat'], rtol=tol, atol=0) and
            np.isclose(old_results['b_lat'], new_results['b_lat'], rtol=tol, atol=0) and
            np.isclose(old_results['c_lat'], new_results['c_lat'], rtol=tol, atol=0)):
            converged = True
            break
        else:
            old_results = new_results    
    
    # Return values if converged
    if converged:
        # Scale lattice constants to ucell 
        new_results['a_lat'] = new_results['a_lat'] / lx_a
        new_results['b_lat'] = new_results['b_lat'] / ly_b
        new_results['c_lat'] = new_results['c_lat'] / lz_c
        
        return new_results
    else:
        raise RuntimeError('Failed to converge after 100 cycles')
        
def lammps_ELASTIC(lammps_command, system, potential, symbols, 
                   mpi_command=None, ucell=None,
                   strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, 
                   dmax=0.01, pressure_unit='GPa'):
    """Sets up and runs the ELASTIC example distributed with LAMMPS"""

    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_b = system.box.b / ucell.box.b
    lz_c = system.box.c / ucell.box.c
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Define lammps variables
    lammps_variables = {}
    
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', units=potential.units, atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['strainrange'] = strainrange
    lammps_variables['pressure_unit_scaling'] = uc.get_in_units(uc.set_in_units(1.0, lammps_units['pressure']), pressure_unit)
    lammps_variables['pressure_unit'] = pressure_unit
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Fill in mod.template files
    with open('init.mod.template') as template_file:
        template = template_file.read()
    with open('init.mod', 'w') as in_file:
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    with open('potential.mod.template') as template_file:
        template = template_file.read()
    with open('potential.mod', 'w') as in_file:
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))    
    
    output = lmp.run(lammps_command, 'in.elastic', mpi_command)
    
    # Extract output values
    thermo = output.simulations[0]['thermo']
    
    results = {}
    results['E_coh'] = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy']) / system.natoms
    results['a_lat'] = uc.set_in_units(thermo.Lx.values[-1], lammps_units['length']) / lx_a
    results['b_lat'] = uc.set_in_units(thermo.Ly.values[-1], lammps_units['length']) / ly_b
    results['c_lat'] = uc.set_in_units(thermo.Lz.values[-1], lammps_units['length']) / lz_c
    results['alpha_lat'] = alpha
    results['beta_lat'] =  beta
    results['gamma_lat'] = gamma
    
    pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
    results['stress'] = -1 * np.array([[pxx, pxy, pxz],
                                       [pxy, pyy, pyz],
                                       [pxz, pyz, pzz]])
    
    # Load relaxed system from dump file
    last_dump_file = 'atom.'+str(thermo.Step.values[-1])
    results['system_relaxed'] = lmp.atom_dump.load(last_dump_file) 
    
    with open('log.lammps') as log_file:
        log = log_file.read()
    
    start = log.find('print "Elastic Constant C11all = ${C11all} ${cunits}"')
    lines = log[start+54:].split('\n')

    Cdict = {}
    for line in lines:
        terms = line.split()
        if len(terms) > 0 and terms[0] == 'Elastic':
            c_term = terms[2][:3]
            c_value = float(terms[4])
            c_unit = terms[5]
            
            Cdict[c_term] = uc.set_in_units(c_value, c_unit)
    results['C_elastic'] = am.ElasticConstants(**Cdict)
                
    return results

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
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    input_dict['convergevalues'] = iprPy.input.boolean(input_dict.get('convergevalues', True))
    
    # These are calculation-specific default integers
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  1000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 10000))
    
    # These are calculation-specific default unitless floats
    input_dict['strainrange'] =     float(input_dict.get('strainrange',     1e-6))
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    input_dict['temperature'] = 0.0
    input_dict['pressure_xx'] = 0.0
    input_dict['pressure_yy'] = 0.0
    input_dict['pressure_zz'] = 0.0
    
    # These are calculation-specific default floats with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-10 eV/angstrom')
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
if __name__ == '__main__':
    main(*sys.argv[1:]) 