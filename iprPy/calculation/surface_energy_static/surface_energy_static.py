# coding: utf-8

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from pathlib import Path
import shutil
import datetime

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from ...tools import filltemplate, read_calc_file

# Define calculation metadata
parent_module = '.'.join(__name__.split('.')[:-1])

def surface_energy_static(lammps_command, ucell, potential, hkl,
                   mpi_command=None, sizemults=None, minwidth=None, even=False,
                   conventional_setting='p', cutboxvector='c', 
                   atomshift=None, shiftindex=None,
                   etol=0.0, ftol=0.0, maxiter=10000,
                   maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Evaluates surface formation energies by slicing along one periodic
    boundary of a bulk system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the stacking fault
        configurations.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    hkl : array-like object
        The Miller(-Bravais) crystal fault plane relative to ucell.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sizemults : list or tuple, optional
        The three System.supersize multipliers [a_mult, b_mult, c_mult] to use on the
        rotated cell to build the final system. Note that the cutboxvector sizemult
        must be an integer and not a tuple.  Default value is [1, 1, 1].
    minwidth : float, optional
        If given, the sizemult along the cutboxvector will be selected such that the
        width of the resulting final system in that direction will be at least this
        value. If both sizemults and minwidth are given, then the larger of the two
        in the cutboxvector direction will be used. 
    even : bool, optional
        A True value means that the sizemult for cutboxvector will be made an even
        number by adding 1 if it is odd.  Default value is False.
    conventional_setting : str, optional
        Allows for rotations of a primitive unit cell to be determined from
        (hkl) indices specified relative to a conventional unit cell.  Allowed
        settings: 'p' for primitive (no conversion), 'f' for face-centered,
        'i' for body-centered, and 'a', 'b', or 'c' for side-centered.  Default
        behavior is to perform no conversion, i.e. take (hkl) relative to the
        given ucell.
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', to
        cut with a non-periodic boundary (default is 'c').
    atomshift : array-like object, optional
        A Cartesian vector shift to apply to all atoms.  Can be used to shift
        atoms perpendicular to the fault plane to allow different termination
        planes to be cut.  Cannot be given with shiftindex.
    shiftindex : int, optional
        Allows for selection of different termination planes based on the
        preferred shift values determined by the underlying fault generation.
        Cannot be given with atomshift. If neither atomshift nor shiftindex
        given, then shiftindex will be set to 0.
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
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed bulk system.
        - **'dumpfile_surf'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed system containing the free surfaces.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_surf'** (*float*) - The total potential energy of the
          relaxed system containing the free surfaces.
        - **'A_surf'** (*float*) - The area of the free surface.
        - **'E_coh'** (*float*) - The cohesive energy of the relaxed bulk
          system.
        - **'E_surf_f'** (*float*) - The computed surface formation energy.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors
    """
    # Construct free surface configuration generator
    surf_gen = am.defect.FreeSurface(hkl, ucell, cutboxvector=cutboxvector,
                                     conventional_setting=conventional_setting)

    # Check shift parameters
    if shiftindex is not None:
        assert atomshift is None, 'shiftindex and atomshift cannot both be given'
        atomshift = surf_gen.shifts[shiftindex]
    elif atomshift is None:
        atomshift = surf_gen.shifts[0]

    # Generate the free surface configuration
    system = surf_gen.surface(shift=atomshift, minwidth=minwidth,
                                  sizemults=sizemults, even=even)
    A_surf= surf_gen.surfacearea

    # Identify lammps_date version
    lammps_date = lmp.checkversion(lammps_command)['date']

    # Evaluate system with free surface
    surf_results = relax_system(lammps_command, system, potential,
                                mpi_command=mpi_command, etol=etol, ftol=ftol,
                                maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                                lammps_date=lammps_date)
    
    # Extract results from system with free surface
    dumpfile_surf = 'surface.dump'
    shutil.move(surf_results['finaldumpfile'], dumpfile_surf)
    shutil.move('log.lammps', 'surface-log.lammps')
    E_total_surf = surf_results['potentialenergy']

    # Evaluate perfect system (all pbc removes cut)
    system.pbc = [True, True, True]
    perf_results = relax_system(lammps_command, system, potential,
                                mpi_command=mpi_command, etol=etol, ftol=ftol,
                                maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                                lammps_date=lammps_date)
    
    # Extract results from perfect system
    dumpfile_base = 'perfect.dump'
    shutil.move(perf_results['finaldumpfile'], dumpfile_base)
    shutil.move('log.lammps', 'perfect-log.lammps')
    E_total_base = perf_results['potentialenergy']
    
    # Compute the free surface formation energy
    E_surf_f = (E_total_surf - E_total_base) / (2 * A_surf)
    
    # Save values to results dictionary
    results_dict = {}
    
    results_dict['dumpfile_base'] = dumpfile_base
    results_dict['dumpfile_surf'] = dumpfile_surf
    results_dict['E_total_base'] = E_total_base
    results_dict['E_total_surf'] = E_total_surf
    results_dict['A_surf'] = A_surf
    results_dict['E_coh'] = E_total_base / system.natoms
    results_dict['E_surf_f'] = E_surf_f
    
    return results_dict

def relax_system(lammps_command, system, potential,
                 mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000,
                 maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
                 lammps_date=None):
    """
    Sets up and runs the min.in LAMMPS script for performing an energy/force
    minimization to relax a system.
    
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
        
        - **'logfile'** (*str*) - The name of the LAMMPS log file.
        - **'initialdatafile'** (*str*) - The name of the LAMMPS data file
          used to import an inital configuration.
        - **'initialdumpfile'** (*str*) - The name of the LAMMPS dump file
          corresponding to the inital configuration.
        - **'finaldumpfile'** (*str*) - The name of the LAMMPS dump file
          corresponding to the relaxed configuration.
        - **'potentialenergy'** (*float*) - The total potential energy of
          the relaxed system.
    """
    
    # Ensure all atoms are within the system's box
    system.wrap()
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
      
    #Get lammps version date
    if lammps_date is None:
        lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='system.dat',
                              potential=potential,
                              return_pair_info=True)
    lammps_variables['atomman_system_pair_info'] = system_info
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
    template_file = 'min.template'
    lammps_script = 'min.in'
    template = read_calc_file(parent_module, template_file)
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    results = {}
    results['logfile'] = 'log.lammps'
    results['initialdatafile'] = 'system.dat'
    results['initialdumpfile'] = 'atom.0'
    results['finaldumpfile'] = 'atom.%i' % thermo.Step.values[-1]
    results['potentialenergy'] = uc.set_in_units(thermo.PotEng.values[-1],
                                                 lammps_units['energy'])
    
    return results