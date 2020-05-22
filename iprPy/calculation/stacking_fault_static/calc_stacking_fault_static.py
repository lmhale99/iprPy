#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from pathlib import Path
import sys
import uuid
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

# Define calculation metadata
calculation_style = 'stacking_fault_static'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    results_dict = stackingfault(input_dict['lammps_command'],
                                 input_dict['initialsystem'],
                                 input_dict['potential'],
                                 mpi_command = input_dict['mpi_command'],
                                 a1vect = input_dict['shiftvector1'],
                                 a2vect = input_dict['shiftvector2'],
                                 ucell = input_dict['ucell'],
                                 transform = input_dict['transformationmatrix'],
                                 cutboxvector = input_dict['stackingfault_cutboxvector'],
                                 faultposrel = input_dict['faultpos'],
                                 a1 = input_dict['stackingfault_shiftfraction1'],
                                 a2 = input_dict['stackingfault_shiftfraction2'],
                                 etol = input_dict['energytolerance'],
                                 ftol = input_dict['forcetolerance'],
                                 maxiter = input_dict['maxiterations'],
                                 maxeval = input_dict['maxevaluations'],
                                 dmax = input_dict['maxatommotion'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def stackingfaultrelax(lammps_command, system, potential,
                       mpi_command=None, sim_directory=None,
                       cutboxvector='c',
                       etol=0.0, ftol=0.0,
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
        The system containing a stacking fault.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simulation in.  If not
        given, will use the current working directory.
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', has
        the non-periodic boundary (default is 'c').  Fault plane normal is
        defined by the cross of the other two box vectors.
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
    lammps_date : datetime.date or None, optional
        The date version of the LAMMPS executable.  If None, will be identified
        from the lammps_command (default is None).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'logfile'** (*str*) - The filename of the LAMMPS log file.
        - **'dumpfile'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed system.
        - **'system'** (*atomman.System*) - The relaxed system.
        - **'E_total'** (*float*) - The total potential energy of the relaxed
          system.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}
    
    # Give correct LAMMPS fix setforce command
    if cutboxvector == 'a':
        fix_cut_setforce = 'fix cut all setforce NULL 0 0'    
    elif cutboxvector == 'b':
        fix_cut_setforce = 'fix cut all setforce 0 NULL 0'
    elif cutboxvector == 'c':
        fix_cut_setforce = 'fix cut all setforce 0 0 NULL'    
    else: 
        raise ValueError('Invalid cutboxvector')
    
    if sim_directory is not None:
        # Create sim_directory if it doesn't exist
        sim_directory = Path(sim_directory)
        if not sim_directory.is_dir():
            sim_directory.mkdir()
        sim_directory = sim_directory.as_posix()+'/'
    else:
        # Set sim_directory if is None
        sim_directory = ''
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    if lammps_date is None:
        lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data',
                              f=Path(sim_directory, 'system.dat').as_posix(),
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
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
    lammps_script = Path(sim_directory, 'sfmin.in')
    template = iprPy.tools.read_calc_file(template_file, filedict)
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script.as_posix(), mpi_command,
                     logfile=Path(sim_directory, 'log.lammps').as_posix())
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    logfile = Path(sim_directory, 'log.lammps').as_posix()
    dumpfile = Path(sim_directory, f'{thermo.Step.values[-1]}.dump').as_posix()
    E_total = uc.set_in_units(thermo.PotEng.values[-1],
                              lammps_units['energy'])
    
    # Load relaxed system
    system = am.load('atom_dump', dumpfile, symbols=system.symbols)
    
    # Return results
    results_dict = {}
    results_dict['logfile'] = logfile
    results_dict['dumpfile'] = dumpfile
    results_dict['system'] = system
    results_dict['E_total'] = E_total
    
    return results_dict

def stackingfault(lammps_command, system, potential, 
                  mpi_command=None,
                  a1vect=None, a2vect=None, ucell=None,
                  transform=None, cutboxvector=None,
                  faultposrel=0.5, a1=0.0, a2=0.0, 
                  etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
                  dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Computes the generalized stacking fault value for a single faultshift.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    a1vect : array-like object, optional
        A slip vector within the slip plane.  Depending on if ucellbox and
        transform are given, this can be either a Miller crystal vector or
        a Cartesian vector relative to the supplied system.  If a1vect is
        not given and a2vect is, then a1vect is set to [0,0,0].
    a2vect : array-like object, optional
        A slip vector within the slip plane.  Depending on if ucellbox and
        transform are given, this can be either a Miller crystal vector or
        a Cartesian vector relative to the supplied system.  If a2vect is
        not given and a1vect is, then a2vect is set to [0,0,0].
    ucell : atomman.System, optional
        If ucell is given, then the a1vect and a2vect slip vectors are
        taken as Miller crystal vectors relative to ucell.box.  If not
        given, then the slip vectors are taken as Cartesian vectors.
    transform : array-like object, optional
        A transformation tensor to apply to the a1vect and a2vect slip
        vectors.  This is needed if system is oriented differently than
        ucell, i.e. system is rotated.
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', to
        cut with a non-periodic boundary (default is 'c').
    faultposrel : float, optional
        The fractional position along the cutboxvector where the stacking
        fault plane will be placed (default is 0.5).
    a1 : float, optional
        The fractional coordinate of a1vect to shift by. 
        Default value is 0.0.
    a2 : float, optional
        The fractional coordinate of a2vect to shift by. 
        Default value is 0.0. 
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
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_gsf'** (*float*) - The stacking fault formation energy.
        - **'E_total_0'** (*float*) - The total potential energy of the
          system before applying the faultshift.
        - **'E_total_sf'** (*float*) - The total potential energy of the
          system after applying the faultshift.
        - **'delta_disp'** (*float*) - The change in the center of mass
          difference between before and after applying the faultshift.
        - **'disp_0'** (*float*) - The center of mass difference between atoms
          above and below the fault plane in the cutboxvector direction for
          the system before applying the faultshift.
        - **'disp_sf'** (*float*) - The center of mass difference between 
          atoms above and below the fault plane in the cutboxvector direction
          for the system after applying the faultshift.
        - **'A_fault'** (*float*) - The area of the fault surface.
        - **'dumpfile_0'** (*str*) - The name of the LAMMMPS dump file
          associated with the relaxed system before applying the faultshift.
        - **'dumpfile_sf'** (*str*) - The name of the LAMMMPS dump file
          associated with the relaxed system after applying the faultshift.
    """
    # Construct stacking fault configuration generator
    gsf_gen = am.defect.StackingFault(system, a1vect=a1vect, a2vect=a2vect,
                                      ucellbox=ucell.box, transform=transform,
                                      cutboxvector=cutboxvector, faultposrel=faultposrel)
    abovefault = gsf_gen.abovefault
    cutindex = gsf_gen.cutindex
    A_fault = gsf_gen.faultarea

    # Evaluate the system without shifting along the fault plane
    sfsystem = gsf_gen.fault(a1=0.0, a2=0.0)
    zeroshift = stackingfaultrelax(lammps_command, sfsystem, potential,
                                   mpi_command=mpi_command,
                                   cutboxvector=cutboxvector,
                                   etol=etol, ftol=ftol, maxiter=maxiter,
                                   maxeval=maxeval, dmax=dmax)
    
    # Extract terms
    E_total_0 = zeroshift['E_total']
    pos_0 = zeroshift['system'].atoms.pos
    shutil.move('log.lammps', 'zeroshift-log.lammps')
    shutil.move(zeroshift['dumpfile'], 'zeroshift.dump')

    # Evaluate the system after shifting along the fault plane
    sfsystem = gsf_gen.fault(a1=a1, a2=a2)
    shifted = stackingfaultrelax(lammps_command, sfsystem, potential,
                                 mpi_command=mpi_command,
                                 cutboxvector=cutboxvector,
                                 etol=etol, ftol=ftol, maxiter=maxiter,
                                 maxeval=maxeval, dmax=dmax)
    
    # Extract terms
    E_total_sf = shifted['E_total']
    pos_sf = shifted['system'].atoms.pos
    shutil.move('log.lammps', 'shifted-log.lammps')
    shutil.move(shifted['dumpfile'], 'shifted.dump')

    # Compute the stacking fault energy
    E_gsf = (E_total_sf - E_total_0) / A_fault
    
    # Compute the change in displacement normal to fault plane
    disp_0 = (pos_0[abovefault, cutindex].mean()
            - pos_0[~abovefault, cutindex].mean())
    disp_sf = (pos_sf[abovefault, cutindex].mean()
             - pos_sf[~abovefault, cutindex].mean())
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
    # Set script's name
    input_dict['script'] = script
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    input_dict['stackingfault_shiftfraction1'] = float(input_dict.get('stackingfault_shiftfraction1', 0.0))
    input_dict['stackingfault_shiftfraction2'] = float(input_dict.get('stackingfault_shiftfraction2', 0.0))
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.subset('lammps_minimize').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)
    
    # Load stackingfault parameters
    iprPy.input.subset('stackingfault').interpret(input_dict)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)
    
    # Convert stackingfault parameters
    iprPy.input.subset('stackingfault').interpret2(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])