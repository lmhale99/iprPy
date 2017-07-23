#!/usr/bin/env python

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from __future__ import division, absolute_import, print_function
import os
import sys
import uuid
import shutil
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np 

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calc_style and record_style
calc_style = 'stacking_fault_multi'
record_style = 'calculation_generalized_stacking_fault'

def main(*args):
    """Main function called when script is executed directly."""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    results_dict = stackingfaultmap(input_dict['lammps_command'],
                                     input_dict['initialsystem'],
                                     input_dict['potential'],
                                     input_dict['symbols'],
                                     input_dict['shiftvector1'],
                                     input_dict['shiftvector2'],
                                     mpi_command = input_dict['mpi_command'],
                                     numshifts1 = input_dict['stackingfault_numshifts1'],
                                     numshifts2 = input_dict['stackingfault_numshifts2'],
                                     cutboxvector = input_dict['stackingfault_cutboxvector'],
                                     faultpos = input_dict['faultpos'],
                                     etol = input_dict['energytolerance'],
                                     ftol = input_dict['forcetolerance'],
                                     maxiter = input_dict['maxiterations'],
                                     maxeval = input_dict['maxevaluations'],
                                     dmax = input_dict['maxatommotion'])

    # Save data model of results
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                               results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def stackingfaultpoint(lammps_command, system, potential, symbols,
                       mpi_command=None, sim_directory=None,
                       cutboxvector='c', faultpos=0.5,
                       faultshift=[0.0, 0.0, 0.0], etol=0.0, ftol=0.0,
                       maxiter=10000, maxeval=100000,
                       dmax=uc.set_in_units(0.01, 'angstrom'),
                       lammps_date=None):
    """
    Perform a stacking fault relaxation simulation for a single faultshift.
    
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
    sim_directory : str, optional
        The path to the directory to perform the simuation in.  If not
        given, will use the current working directory.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', to
        cut with a non-periodic boundary (default is 'c').
    faultpos : float, optional
        The fractional position along the cutboxvector where the stacking
        fault plane will be placed (default is 0.5).
    faultshift : list of float, optional
        The vector shift to apply to all atoms above the fault plane defined
        by faultpos (default is [0,0,0], i.e. no shift applied).
    lammps_date : datetime.date or None, optional
        The date version of the LAMMPS executable.  If None, will be identified from the lammps_command (default is None).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'logfile'** (*str*) - The filename of the LAMMPS log file.
        - **'dumpfile'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed system.
        - **'system'** (*atomman.System*) - The relaxed system.
        - **'A_fault'** (*float*) - The area of the fault surface.
        - **'E_total'** (*float*) - The total potential energy of the relaxed
          system.
        - **'disp'** (*float*) - The center of mass difference between atoms
          above and below the fault plane in the cutboxvector direction.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors.
    """
    
    # Set options based on cutboxvector
    if cutboxvector == 'a':
        # Assert system is compatible with planeaxis value
        if system.box.xy != 0.0 or system.box.xz != 0.0:
            raise ValueError("box tilts xy and xz must be 0 for cutboxvector='a'")
        
        # Specify cutindex
        cutindex = 0
        
        # Identify atoms above fault
        faultpos = system.box.xlo + system.box.lx * faultpos
        abovefault = system.atoms.view['pos'][:, cutindex] > (faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.bvect,
                                            system.box.cvect))
        
        # Give correct LAMMPS fix setforce command
        fix_cut_setforce = 'fix cut all setforce NULL 0 0'
        
    elif cutboxvector == 'b':
        # Assert system is compatible with planeaxis value
        if system.box.yz != 0.0:
            raise ValueError("box tilt yz must be 0 for cutboxvector='b'")
        
        # Specify cutindex
        cutindex = 1
        
        # Identify atoms above fault
        faultpos = system.box.ylo + system.box.ly * faultpos
        abovefault = system.atoms.view['pos'][:, cutindex] > (faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect,
                                            system.box.cvect))
        
        # Give correct LAMMPS fix setforce command
        fix_cut_setforce = 'fix cut all setforce 0 NULL 0'
        
    elif cutboxvector == 'c':
        # Specify cutindex
        cutindex = 2
        
        # Identify atoms above fault
        faultpos = system.box.zlo + system.box.lz * faultpos
        abovefault = system.atoms.view['pos'][:, cutindex] > (faultpos)
        
        # Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect,
                                            system.box.bvect))
        
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
       
    #Get lammps version date
    if lammps_date is None:
        lammps_date = iprPy.tools.check_lammps_version(lammps_command)['lammps_date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = lmp.atom_data.dump(sfsystem,
                                     os.path.join(sim_directory,
                                                  'system.dat'),
                                     units=potential.units,
                                     atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['fix_cut_setforce'] = fix_cut_setforce
    lammps_variables['sim_directory'] = sim_directory
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%i %i %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
        
    # Write lammps input script
    template_file = 'sfmin.template'
    lammps_script = os.path.join(sim_directory, 'sfmin.in')
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command,
                     return_style='object',
                     logfile=os.path.join(sim_directory, 'log.lammps'))
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    logfile = os.path.join(sim_directory, 'log.lammps')
    dumpfile = os.path.join(sim_directory, '%i.dump' % thermo.Step.values[-1])
    E_total = uc.set_in_units(thermo.PotEng.values[-1],
                              lammps_units['energy'])
    
    #Load relaxed system
    sfsystem = lmp.atom_dump.load(dumpfile)
              
    # Find center of mass difference in top/bottom planes
    disp = (sfsystem.atoms.view['pos'][abovefault, cutindex].mean()
            - sfsystem.atoms.view['pos'][~abovefault, cutindex].mean())
    
    # Return results
    results_dict = {}
    results_dict['logfile'] = logfile
    results_dict['dumpfile'] = dumpfile
    results_dict['system'] = sfsystem
    results_dict['A_fault'] = faultarea
    results_dict['E_total'] = E_total
    results_dict['disp'] = disp
    
    return results_dict
    
def stackingfaultworker(lammps_command, system, potential, symbols,
                        shiftvector1, shiftvector2, shiftfraction1,
                        shiftfraction2, mpi_command=None, cutboxvector=None,
                        faultpos=0.5, etol=0.0, ftol=0.0, maxiter=10000,
                        maxeval=100000, 
                        dmax=uc.set_in_units(0.01, 'angstrom'),
                        lammps_date=None):
    """
    A wrapper function around stackingfaultpoint. Converts
    shiftfractions and shiftvectors to a faultshift, runs stackingfaultpoint,
    and adds keys 'shift1' and 'shift2' to the returned dictionary
    corresponding to the shiftfractions.
    """
    
    # Compute the faultshift
    faultshift = shiftfraction1*shiftvector1 + shiftfraction2*shiftvector2

    # Name the simulation directory based on shiftfractions
    sim_directory = 'a%.10f-b%.10f' % (shiftfraction1, shiftfraction2)

    # Evaluate the system at the shift
    sf = stackingfaultpoint(lammps_command, system, potential, symbols,
                            mpi_command=mpi_command,
                            cutboxvector=cutboxvector,
                            faultpos=faultpos,
                            etol=etol,
                            ftol=ftol,
                            maxiter=maxiter,
                            maxeval=maxeval,
                            dmax=dmax,
                            faultshift=faultshift,
                            sim_directory=sim_directory,
                            lammps_date=lammps_date)
    
    # Add shiftfractions to sf results
    sf['shift1'] = shiftfraction1
    sf['shift2'] = shiftfraction2
    
    return sf
    
def stackingfaultmap(lammps_command, system, potential, symbols,
                     shiftvector1, shiftvector2, mpi_command=None,
                     numshifts1=11, numshifts2=11,
                     cutboxvector=None, faultpos=0.5,
                     etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
                     dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Computes a generalized stacking fault map for shifts along a regular 2D
    grid.
    
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
    shiftvector1 : list of floats or numpy.array
        One of the generalized stacking fault shifting vectors.
    shiftvector2 : list of floats or numpy.array
        One of the generalized stacking fault shifting vectors.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', to
        cut with a non-periodic boundary (default is 'c').
    numshifts1 : int, optional
        The number of equally spaced shiftfractions to evaluate along
        shiftvector1.
    numshifts2 : int, optional
        The number of equally spaced shiftfractions to evaluate along
        shiftvector2.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'shift1'** (*numpy.array of float*) - The fractional shifts along
          shiftvector1 where the stacking fault was evaluated.
        - **'shift2'** (*numpy.array of float*) - The fractional shifts along
          shiftvector2 where the stacking fault was evaluated.
        - **'E_gsf'** (*numpy.array of float*) - The stacking fault formation
          energies measured for all the (shift1, shift2) coordinates.
        - **'delta_disp'** (*numpy.array of float*) - The change in the center
          of mass difference between before and after applying the faultshift
          for all the (shift1, shift2) coordinates.
        - **'A_fault'** (*float*) - The area of the fault surface.
    """
   
    # Start sf_df as empty list
    sf_df = []

    # Construct mesh of regular points
    shifts1, shifts2 = np.meshgrid(np.linspace(0, 1, numshifts1),
                                   np.linspace(0, 1, numshifts2))
    
    # Identify lammps_date version
    lammps_date = iprPy.tools.check_lammps_version(lammps_command)['lammps_date']
    
    # Loop over all shift combinations
    for shiftfraction1, shiftfraction2 in zip(shifts1.flat, shifts2.flat):
        
        # Evaluate the system at the shift
        sf_df.append(stackingfaultworker(lammps_command, system, potential,
                                         symbols,
                                         shiftvector1, shiftvector2,
                                         shiftfraction1, shiftfraction2,
                                         mpi_command=mpi_command,
                                         cutboxvector=cutboxvector,
                                         faultpos=faultpos,
                                         etol=etol,
                                         ftol=ftol,
                                         maxiter=maxiter,
                                         maxeval=maxeval,
                                         dmax=dmax,
                                         lammps_date=lammps_date))
    
    # Convert sf_df to pandas DataFrame
    sf_df = pd.DataFrame(sf_df)

    # Identify the zeroshift column
    zeroshift = sf_df[(np.isclose(sf_df.shift1, 0.0, atol=1e-10, rtol=0.0)
                     & np.isclose(sf_df.shift2, 0.0, atol=1e-10, rtol=0.0))]
    assert len(zeroshift) == 1, 'zeroshift simulation not uniquely identified'
    
    # Get zeroshift values
    E_total_0 = zeroshift.E_total.values[0]
    A_fault = zeroshift.A_fault.values[0]
    disp_0 = zeroshift.disp.values[0]
    
    # Compute the stacking fault energy
    E_gsf = (sf_df.E_total.values - E_total_0) / A_fault
    
    # Compute the change in displacement normal to fault plane
    delta_disp = sf_df.disp.values - disp_0
    
    results_dict = {}
    results_dict['shift1'] = sf_df.shift1.values
    results_dict['shift2'] = sf_df.shift2.values
    results_dict['E_gsf'] = E_gsf
    results_dict['delta_disp'] = delta_disp
    results_dict['A_fault'] = A_fault
    
    return results_dict
    
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
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['stackingfault_numshifts1'] = int(input_dict.get('stackingfault_numshifts1', 11))
    input_dict['stackingfault_numshifts2'] = int(input_dict.get('stackingfault_numshifts2', 11))
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
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
    
    # Load stackingfault parameters
    iprPy.input.stackingfault1(input_dict)
    
    # Load elastic constants
    iprPy.input.elasticconstants(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
    # Convert stackingfault parameters
    iprPy.input.stackingfault2(input_dict, build=build)
    
if __name__ == '__main__':
    main(*sys.argv[1:])