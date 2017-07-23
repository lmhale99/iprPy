#!/usr/bin/env python

# Python script created by Lucas Hale
# Built around LAMMPS script by Steve Plimpton

# Standard library imports
from __future__ import division, absolute_import, print_function
import os
import sys
import uuid
import glob
import shutil
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
calc_style = 'LAMMPS_ELASTIC'
record_style = 'calculation_system_relax'

def main(*args):
    """Main function called when script is executed directly."""
    
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
                                             mpi_command = input_dict['mpi_command'],
                                             ucell = input_dict['ucell'],
                                             strainrange = input_dict['strainrange'],
                                             etol = input_dict['energytolerance'],
                                             ftol = input_dict['forcetolerance'],
                                             maxiter = input_dict['maxiterations'],
                                             maxeval = input_dict['maxevaluations'],
                                             dmax = input_dict['maxatommotion'],
                                             pressure_unit = input_dict['pressure_unit'])
    else:
        # Run lammps_ELASTIC to refine values
        results_dict = lammps_ELASTIC(input_dict['lammps_command'], 
                                      input_dict['initialsystem'],
                                      input_dict['potential'],
                                      input_dict['symbols'],
                                      mpi_command = input_dict['mpi_command'],
                                      ucell = input_dict['ucell'],
                                      strainrange = input_dict['strainrange'],
                                      etol = input_dict['energytolerance'],
                                      ftol = input_dict['forcetolerance'],
                                      maxiter = input_dict['maxiterations'],
                                      maxeval = input_dict['maxevaluations'],
                                      dmax = input_dict['maxatommotion'],
                                      pressure_unit = input_dict['pressure_unit'])
                                  
    # Save data model of results
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                               results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def lammps_ELASTIC_refine(lammps_command, system, potential, symbols,
                          mpi_command=None, ucell=None,
                          strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=10000,
                          maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
                          pressure_unit='GPa', tol=1e-10):
    """
    Repeatedly runs the ELASTIC example distributed with LAMMPS until box
    dimensions converge within a tolerance.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list of str
        The list of element-model symbols for the Potential that correspond to
        system's atypes.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    ucell : atomman.System, optional
        The fundamental unit cell correspodning to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    strainrange : float, optional
        The small strain value to apply when calculating the elastic
        constants (default is 1e-6).
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    pressure_unit : str, optional
        The unit of pressure to calculate the elastic constants in (default is
        'GPa').
    tol : float, optional
        The relative tolerance used to determine if the lattice constants have
        converged (default is 1e-10).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'a_lat'** (*float*) - The relaxed a lattice constant.
        - **'b_lat'** (*float*) - The relaxed b lattice constant.
        - **'c_lat'** (*float*) - The relaxed c lattice constant.
        - **'alpha_lat'** (*float*) - The alpha lattice angle.
        - **'beta_lat'** (*float*) - The beta lattice angle.
        - **'gamma_lat'** (*float*) - The gamma lattice angle.
        - **'E_coh'** (*float*) - The cohesive energy of the relaxed system.
        - **'stress'** (*numpy.array*) - The measured stress state of the
          relaxed system.
        - **'C_elastic'** (*atomman.ElasticConstants*) - The relaxed system's
          elastic constants.
        - **'system_relaxed'** (*atomman.System*) - The relaxed system.
    """
    
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
                                 strainrange=strainrange,
                                 etol=etol, ftol=ftol,
                                 maxiter=maxiter, maxeval=maxeval,
                                 dmax=dmax, pressure_unit=pressure_unit)
    shutil.move('log.lammps', 'elastic-0-log.lammps')
    os.remove('atom.0')
    for atom_dump in glob.iglob('atom.*'):
        shutil.move(atom_dump, 'elastic-0-config.dump')
    
    converged = False
    for cycle in xrange(1, 100):
        new_results = lammps_ELASTIC(lammps_command,
                                     old_results['system_relaxed'],
                                     potential, symbols, 
                                     mpi_command=mpi_command,
                                     ucell=None,
                                     strainrange=strainrange,
                                     etol=etol, ftol=ftol, 
                                     maxiter=maxiter, maxeval=maxeval,
                                     dmax=dmax, pressure_unit=pressure_unit)
        shutil.move('log.lammps', 'elastic-'+str(cycle)+'-log.lammps')
        os.remove('atom.0')
        for atom_dump in glob.iglob('atom.*'):
            shutil.move(atom_dump, 'elastic-'+str(cycle)+'-config.dump')
        
        # Test if box dimensions have converged
        if (np.isclose(old_results['a_lat'],
                       new_results['a_lat'],
                       rtol=tol, atol=0)
          and
            np.isclose(old_results['b_lat'],
                       new_results['b_lat'],
                       rtol=tol, atol=0)
          and
            np.isclose(old_results['c_lat'],
                       new_results['c_lat'],
                       rtol=tol, atol=0)):
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
                   strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=10000,
                   maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
                   pressure_unit='GPa'):
    """
    Sets up and runs the ELASTIC example distributed with LAMMPS.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list of str
        The list of element-model symbols for the Potential that correspond to
        system's atypes.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    ucell : atomman.System, optional
        The fundamental unit cell correspodning to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    strainrange : float, optional
        The small strain value to apply when calculating the elastic
        constants (default is 1e-6).
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is 
        0.01 Angstroms).
    pressure_unit : str, optional
        The unit of pressure to calculate the elastic constants in (default is
        'GPa').
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'a_lat'** (*float*) - The relaxed a lattice constant.
        - **'b_lat'** (*float*) - The relaxed b lattice constant.
        - **'c_lat'** (*float*) - The relaxed c lattice constant.
        - **'alpha_lat'** (*float*) - The alpha lattice angle.
        - **'beta_lat'** (*float*) - The beta lattice angle.
        - **'gamma_lat'** (*float*) - The gamma lattice angle.
        - **'E_coh'** (*float*) - The cohesive energy of the relaxed system.
        - **'stress'** (*numpy.array*) - The measured stress state of the
          relaxed system.
        - **'C_elastic'** (*atomman.ElasticConstants*) - The relaxed system's
          elastic constants.
        - **'system_relaxed'** (*atomman.System*) - The relaxed system.
    """

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
    system_info = lmp.atom_data.dump(system, 'init.dat',
                                     units=potential.units,
                                     atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['strainrange'] = strainrange
    pressure_scale = uc.get_in_units(uc.set_in_units(1.0,
                                                    lammps_units['pressure']),
                                     pressure_unit)
    lammps_variables['pressure_unit_scaling'] = pressure_scale
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
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables,
                                               '<', '>'))
    with open('potential.mod.template') as template_file:
        template = template_file.read()
    with open('potential.mod', 'w') as in_file:
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables,
                                               '<', '>'))
    
    output = lmp.run(lammps_command, 'in.elastic', mpi_command)
    
    # Extract output values
    thermo = output.simulations[0]['thermo']
    
    results = {}
    results['E_coh'] = uc.set_in_units(thermo.PotEng.values[-1] / system.natoms,
                                       lammps_units['energy'])
    results['a_lat'] = uc.set_in_units(thermo.Lx.values[-1] / lx_a,
                                       lammps_units['length'])
    results['b_lat'] = uc.set_in_units(thermo.Ly.values[-1] / ly_b,
                                       lammps_units['length'])
    results['c_lat'] = uc.set_in_units(thermo.Lz.values[-1] / lz_c,
                                       lammps_units['length'])
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
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
                                                  
    # These are calculation-specific default booleans
    input_dict['convergevalues'] = iprPy.input.boolean(input_dict.get('convergevalues', True))
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    input_dict['strainrange'] = float(input_dict.get('strainrange', 1e-6))
    input_dict['temperature'] = 0.0
    input_dict['pressure_xx'] = 0.0
    input_dict['pressure_yy'] = 0.0
    input_dict['pressure_zz'] = 0.0
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.minimize(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
if __name__ == '__main__':
    main(*sys.argv[1:])