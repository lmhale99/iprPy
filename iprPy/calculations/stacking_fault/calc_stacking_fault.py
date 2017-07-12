#!/usr/bin/env python

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
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
calc_style = 'stacking_fault'
record_style = 'calculation-stacking-fault'

def main(*args):
    """Main function for running calculation"""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
    
    results_dict = stackingfault(input_dict['lammps_command'], 
                                 input_dict['initialsystem'], 
                                 input_dict['potential'], 
                                 input_dict['symbols'], 
                                 mpi_command =  input_dict['mpi_command'], 
                                 cutboxvector = input_dict['stackingfault_cutboxvector'], 
                                 faultpos =     input_dict['faultpos'], 
                                 faultshift =   input_dict['faultshift'],
                                 etol =         input_dict['energytolerance'], 
                                 ftol =         input_dict['forcetolerance'], 
                                 maxiter =      input_dict['maxiterations'], 
                                 maxeval =      input_dict['maxevaluations'], 
                                 dmax =         input_dict['maxatommotion'])
    
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def stackingfaultpoint(lammps_command, system, potential, symbols,
                        mpi_command=None, sim_directory=None,
                        cutboxvector='c', faultpos=0.5, faultshift=[0.0, 0.0, 0.0],
                        etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01):
    """Perform a stacking fault relaxation simulation for a single faultshift"""
    
    # Set options based on cutboxvector 
    if cutboxvector == 'a':  
        # Assert system is compatible with planeaxis value
        if system.box.xy != 0.0 or system.box.xz != 0.0:
            raise ValueError("box tilts xy and xz must be 0 for cutboxvector='a'")
        
        # Specify cutindex
        cutindex = 0
        
        # Identify atoms above fault
        abovefault = system.atoms.view['pos'][:, cutindex] > (system.box.xlo + system.box.lx * faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
        
        # Give correct LAMMPS fix setforce command
        fix_cut_setforce = 'fix cut all setforce NULL 0 0'
        
    elif cutboxvector == 'b':  
        # Assert system is compatible with planeaxis value
        if system.box.yz != 0.0:
            raise ValueError("box tilt yz must be 0 for cutboxvector='b'")
        
        # Specify cutindex
        cutindex = 1
        
        # Identify atoms above fault
        abovefault = system.atoms.view['pos'][:, cutindex] > (system.box.ylo + system.box.ly * faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
        
        # Give correct LAMMPS fix setforce command
        fix_cut_setforce = 'fix cut all setforce 0 NULL 0'
        
    elif cutboxvector == 'c':         
        # Specify cutindex
        cutindex = 2
        
        # Identify atoms above fault
        abovefault = system.atoms.view['pos'][:, cutindex] > (system.box.zlo + system.box.lz * faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
        
        # Give correct LAMMPS fix setforce command
        fix_cut_setforce = 'fix cut all setforce 0 0 NULL'
        
    else: 
        raise ValueError('Invalid cutboxvector')
    
    # Assert faultshift is in cut plane
    if faultshift[cutindex] != 0.0:
        raise ValueError('faultshift must be in cut plane')
    
    # Generate stacking fault system by shifting atoms above the fault
    sfsystem = deepcopy(system)
    sfsystem.pbc = [True, True, True]
    sfsystem.pbc[cutindex] = False
    sfsystem.atoms.view['pos'][abovefault] += faultshift
    sfsystem.wrap()
    
    if sim_directory is not None:
        # Create sim_directory if it doesn't exist
        if not os.path.isdir(sim_directory): 
            os.mkdir(sim_directory)
            
        # Add '/' to end of sim_directory string if needed
        if sim_directory[-1] != '/': 
            sim_directory = sim_directory + '/'
    else:
        # Set sim_directory if is None
        sim_directory = ''
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
   
    # Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(sfsystem, 
                                                                 os.path.join(sim_directory, 'system.dat'), 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['fix_cut_setforce'] =  fix_cut_setforce
    lammps_variables['sim_directory'] =     sim_directory   
    lammps_variables['etol'] =              etol
    lammps_variables['ftol'] =              uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] =           maxiter
    lammps_variables['maxeval'] =           maxeval
    lammps_variables['dmax'] =              uc.get_in_units(dmax, lammps_units['length'])
    
    # Set dump_modify format based on LAMMPS version
    dump_modify_version = iprPy.tools.lammps_version.dump_modify(lammps_command)
    if dump_modify_version == 0:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    elif dump_modify_version == 1:
        lammps_variables['dump_modify_format'] = '"%i %i %.13e %.13e %.13e %.13e"'    
        
    # Write lammps input script
    template_file = 'sfmin.template'
    lammps_script = os.path.join(sim_directory, 'sfmin.in')
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object', 
                     logfile=os.path.join(sim_directory, 'log.lammps'))
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    logfile = os.path.join(sim_directory, 'log.lammps')
    dumpfile = os.path.join(sim_directory, '%i.dump' % thermo.Step.values[-1])
    E_total = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    
    #Load relaxed system
    sfsystem = lmp.atom_dump.load(dumpfile)    
              
    # Find center of mass difference in top/bottom planes   
    disp = (sfsystem.atoms.view['pos'][abovefault,  cutindex].mean() -
            sfsystem.atoms.view['pos'][~abovefault, cutindex].mean())
    
    # Return results
    results_dict = {}
    results_dict['logfile'] = logfile
    results_dict['dumpfile'] = dumpfile
    results_dict['system'] = sfsystem
    results_dict['A_fault'] = faultarea
    results_dict['E_total'] = E_total
    results_dict['disp'] = disp 
    
    return results_dict
    
def stackingfault(lammps_command, system, potential, symbols,
                  mpi_command=None, 
                  cutboxvector=None, faultpos=0.5, faultshift=[0.0, 0.0, 0.0],
                  etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01):
    """
    Computes the generalized stacking fault value for a single faultshift
    """
    
    # Evaluate the system without shifting along the fault plane
    zeroshift = stackingfaultpoint(lammps_command, system, potential, symbols,
                                   mpi_command=mpi_command, cutboxvector=cutboxvector, faultpos=faultpos,
                                   etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                                   faultshift=[0.0, 0.0, 0.0])
    
    # Extract terms
    E_total_0 = zeroshift['E_total']
    disp_0 =    zeroshift['disp']
    A_fault =   zeroshift['A_fault']
    shutil.move('log.lammps', 'zeroshift-log.lammps')
    shutil.move(zeroshift['dumpfile'], 'zeroshift.dump')    
    
    # Evaluate the system after shifting along the fault plane
    shifted = stackingfaultpoint(lammps_command, system, potential, symbols,
                                 mpi_command=mpi_command, cutboxvector=cutboxvector, faultpos=faultpos, 
                                 etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                                 faultshift=faultshift)
    
    # Extract terms
    E_total_sf = shifted['E_total']
    disp_sf =    shifted['disp']
    shutil.move('log.lammps', 'shifted-log.lammps')
    shutil.move(shifted['dumpfile'], 'shifted.dump')

    # Compute the stacking fault energy
    E_gsf = (E_total_sf - E_total_0) / A_fault    
    
    # Compute the change in displacement normal to fault plane
    delta_disp = disp_sf - disp_0
    
    # Return processed results
    results = {}
    results['E_gsf'] = E_gsf
    results['E_total_0'] = E_total_0
    results['E_total_sf'] = E_total_sf
    results['delta_disp'] = delta_disp
    results['disp_0'] = disp_0
    results['disp_sf'] = disp_sf
    results['A_fault'] = A_fault
    results['dumpfile_0'] = 'zeroshift.dump'
    results['dumpfile_sf'] = 'shifted.dump'    
    
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
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
    
    # These are calculation-specific default unitless floats
    input_dict['stackingfault_shiftfraction1'] = float(input_dict.get('stackingfault_shiftfraction1', 0.0))
    input_dict['stackingfault_shiftfraction2'] = float(input_dict.get('stackingfault_shiftfraction2', 0.0))
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
    
    # Load stackingfault parameters
    iprPy.input.stackingfault1(input_dict)
    
    # Load elastic constants
    iprPy.input.elasticconstants(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
    # Convert stackingfault parameters
    iprPy.input.stackingfault2(input_dict, build=build)
    
    # Calculate faultshift
    if build is True:
        fraction1 = input_dict['stackingfault_shiftfraction1']
        fraction2 = input_dict['stackingfault_shiftfraction2']
        shiftvector1 = input_dict['shiftvector1']
        shiftvector2 = input_dict['shiftvector2']
        input_dict['faultshift'] = fraction1 * shiftvector1 + fraction2 * shiftvector2
    
    
if __name__ == '__main__':
    main(*sys.argv[1:])