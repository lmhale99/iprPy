#!/usr/bin/env python

# Python script created by Lucas Hale

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
calc_style = 'point_defect_static'
record_style = 'calculation-point-defect-formation'

def main(*args):
    """Main function for running calculation"""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
    
    # Run ptd_energy to refine values
    results_dict = pointdefect(input_dict['lammps_command'], 
                               input_dict['initialsystem'], 
                               input_dict['potential'], 
                               input_dict['symbols'],
                               input_dict['point_kwargs'],
                               mpi_command = input_dict['mpi_command'],
                               etol =        input_dict['energytolerance'], 
                               ftol =        input_dict['forcetolerance'], 
                               maxiter =     input_dict['maxiterations'], 
                               maxeval =     input_dict['maxevaluations'], 
                               dmax =        input_dict['maxatommotion'])
    
    # Run check_ptd_config
    cutoff = 1.05*input_dict['ucell'].box.a
    results_dict.update(check_ptd_config(results_dict['system_ptd'], 
                                         input_dict['point_kwargs'], 
                                         cutoff))
    
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def pointdefect(lammps_command, system, potential, symbols, point_kwargs, mpi_command=None,
               etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy.
    
    Arguments:
    lammps_command -- command for running LAMMPS.
    system -- atomman.System to add the point defect to.
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential.
    symbols -- list of element-model symbols for the Potential that correspond 
               to system's atypes.
    point_kwargs -- dictionary of keyword arguments used by atomman.defect.point
                    for generating a point defect. Multiple defects can be added 
                    simultaneously by providing a list where every entry is a 
                    complete collection of keyword arguments.
    
    Keyword Arguments:
    mpi_command -- MPI command for running LAMMPS in parallel. Default value is
                   None (serial run).  
    etol -- energy tolerance to use for the LAMMPS minimization. Default value 
            is 0.0 (i.e. only uses ftol). 
    ftol -- force tolerance to use for the LAMMPS minimization. Default value 
            is 0.0.
    maxiter -- the maximum number of iterations for the LAMMPS minimization. 
               Default value is 10000.
    maxeval -- the maximum number of evaluations for the LAMMPS minimization. 
               Default value is 100000.    
    dmax -- the maximum distance that an atom is allowed to relax during a 
            minimization iteration. Default value is 0.01 Angstroms.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'perfect.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['etol'] =                etol
    lammps_variables['ftol'] =                uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] =             maxiter
    lammps_variables['maxeval'] =             maxeval
    lammps_variables['dmax'] =                dmax
    
    # Set dump_modify format based on dump_modify_version
    dump_modify_version = iprPy.tools.lammps_version.dump_modify(lammps_command)
    if dump_modify_version == 0:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    elif dump_modify_version == 1:
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    
    # Write lammps input script
    template_file = 'min.template'
    lammps_script = 'min.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps to relax perfect.dat
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract LAMMPS thermo data.
    thermo = output.simulations[0]['thermo']
    E_total_base = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    E_coh = E_total_base / system.natoms
    
    # Rename log file
    shutil.move('log.lammps', 'min-perfect-log.lammps')
    
    # Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(thermo.Step.values[-1])
    system_base = lmp.atom_dump.load(last_dump_file)
    system_base.box_set(vects=system.box.vects)
    lmp.atom_dump.dump(system_base, 'perfect.dump')
    
    # Add defect(s)
    system_ptd = deepcopy(system_base)
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        system_ptd = am.defect.point(system_ptd, **pkwargs)
    
    # Update lammps variables
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system_ptd, 'defect.dat',
                                                                 units = potential.units, 
                                                                 atom_style = potential.atom_style)
    
    # Write lammps input script
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract lammps thermo data
    thermo = output.simulations[0]['thermo']
    E_total_ptd = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    
    # Rename log file
    shutil.move('log.lammps', 'min-defect-log.lammps')    
    
    # Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(thermo.Step.values[-1])
    system_ptd = lmp.atom_dump.load(last_dump_file)
    system_ptd.box_set(vects=system.box.vects)
    
    # Compute defect formation energy as difference between total potential energy of defect system
    # and the cohesive energy of the perfect system times the number of atoms in the defect system
    E_ptd_f = E_total_ptd - E_coh * system_ptd.natoms
    
    # Clear atom.* files and save dump files of relaxed systems
    for fname in glob.iglob(os.path.join(os.getcwd(), 'atom.*')):
        os.remove(fname)
    
    return {'E_coh':         E_coh,          'E_ptd_f':      E_ptd_f, 
            'E_total_base':  E_total_base,   'E_total_ptd':  E_total_ptd,
            'system_base':   system_base,    'system_ptd':   system_ptd,
            'dumpfile_base': 'perfect.dump', 'dumpfile_ptd': 'defect.dump'}

def check_ptd_config(system, point_kwargs, cutoff, tol=uc.set_in_units(1e-5, 'angstrom')):
    """
    Evaluates a relaxed system containing a point defect to determine if the defect 
    structure has transformed to a different configuration.
    
    Arguments:
    system -- atomman.System containing the point defect(s)
    ptd_model -- DataModelDict representation of a point defect data model
    cutoff -- cutoff to use for identifying atoms nearest to the defect's position
    
    Keyword Argument:
    tol -- tolerance to use for identifying if a defect has reconfigured. Default value is 1e-5.
    """
    
    # Check if point_kwargs is a list
    if not isinstance(point_kwargs, (list, tuple)):
        pos = point_kwargs['pos']
    
    # If it is a list of 1, use that set
    elif len(point_kwargs) == 1:
        point_kwargs = point_kwargs[0]
        pos = point_kwargs['pos']
        
    # If it is a list of two (divacancy), use the first and average position
    elif len(point_kwargs) == 2:
        pos = (np.array(point_kwargs[0]['pos']) + np.array(point_kwargs[1]['pos'])) / 2
        point_kwargs = point_kwargs[0]
    
    # More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')

    # Initially set has_reconfigured to False
    has_reconfigured = False
    
    # Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.view['pos'], pos) 
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    
    # Calculate centrosummation by summing up the positions of the close atoms
    centrosummation = np.sum(pos_vects[pos_mags < cutoff], axis=0)
    
    if not np.allclose(centrosummation, np.zeros(3), atol=tol):
        has_reconfigured = True
        
    # Calculate shift of defect atom's position if interstitial or substitutional
    if point_kwargs['ptd_type'] == 'i' or point_kwargs['ptd_type'] == 's':
        position_shift = system.dvect(system.natoms-1, pos)
       
        if not np.allclose(position_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'position_shift':   position_shift}
        
    # Investigate if dumbbell vector has shifted direction 
    elif point_kwargs['ptd_type'] == 'db':
        db_vect = point_kwargs['db_vect'] / np.linalg.norm(point_kwargs['db_vect'])
        new_db_vect = system.dvect(system.natoms-2, system.natoms-1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
    
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'db_vect_shift':    db_vect_shift}   
    
    else:
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation}

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
    input_dict['sizemults'] = input_dict.get('sizemults', '5 5 5')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
    
    # These are calculation-specific default unitless floats
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    
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
    
    # Load point defect parameters
    iprPy.input.pointdefect(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
                
if __name__ == '__main__':
    main(*sys.argv[1:])    