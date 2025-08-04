# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
import datetime
import random
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def dislocation_dipole(lammps_command: str,
                       ucell: am.System,
                       potential: lmp.Potential,
                       C: am.ElasticConstants,
                       burgers: Union[list, np.ndarray],
                       ξ_uvw: Union[list, np.ndarray],
                       slip_hkl: Union[list, np.ndarray],
                       mpi_command: Optional[str] = None,
                       m: Union[list, np.ndarray] = [0,1,0],
                       n: Union[list, np.ndarray] = [0,0,1],
                       conventional_setting: str = 'p',
                       sizemults=None,
                       shift: Union[list, np.ndarray, None] = None,
                       shiftscale: bool = False,
                       shiftindex: int = None,
                       tol: float = 1e-8,
                       etol: float = 0.0,
                       ftol: float = 0.0,
                       maxiter: int = 10000,
                       maxeval: int = 100000,
                       dmax: float = uc.set_in_units(0.01, 'angstrom'),
                       annealtemp: float = 0.0,
                       annealsteps: Optional[int] = None,
                       randomseed: Optional[int] = None,
                       ) -> dict:
    """
    Creates and relaxes a dislocation dipole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The unit cell to use as the seed for generating the dislocation
        monopole system.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    C : atomman.ElasticConstants
        The elastic constants associated with the bulk crystal structure
        for ucell.
    burgers : array-like object
        The dislocation's Burgers vector given as a Miller or
        Miller-Bravais vector relative to ucell.
    ξ_uvw : array-like object
        The dislocation's line direction given as a Miller or
        Miller-Bravais vector relative to ucell.
    slip_hkl : array-like object
        The dislocation's slip plane given as a Miller or Miller-Bravais
        plane relative to ucell.
    mpi_command : str or None, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    m : array-like object, optional
        The m unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,1,0] (y-axis).
    n : array-like object, optional
        The n unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,0,1] (z-axis). n is normal to the dislocation slip plane.
    conventional_setting : str, optional
        Indicates the space lattice setting of the given unit cell, i.e.
        'p' for primitive, 'i' for body-centered, 'f' for face-centered,
        'a', 'b', or 'c' for side-centered and 't1', or 't2' for trigonal
        in a hexagonal setting.  Setting this with the appropriate
        conventional unit cell allows for identifying lattice vectors that
        are not integers with respect to the conventional unit cell.  This
        also creates the rotated cell from a compatible primitive cell,
        thereby the final dislocation configurations can be smaller than
        possible solely from the conventional unit cell.
    sizemults : tuple, optional
        The size multipliers to use when generating the system.  Values are
        limited to being positive integers.  The multipliers for the two
        non-periodic directions must be even.  If not given, the default
        multipliers will be 2 for the non-periodic directions and 1 for the
        periodic direction.
    shift : float, optional
        A rigid body shift to apply to the rotated cell prior to inserting
        the dislocation.  Should be selected such that the ideal slip plane
        does not correspond to any atomic planes.  Is taken as absolute if
        shiftscale is False, or relative to the rotated cell's box vectors
        if shiftscale is True.  Cannot be given with shiftindex.  If
        neither shift nor shiftindex is given then shiftindex = 0 is used.
    shiftindex : float, optional
        The index of the identified optimum shifts based on the rotated
        cell to use.  Different values allow for the selection of different
        atomic planes neighboring the slip plane.  Note that shiftindex
        values only apply shifts normal to the slip plane; best shifts for
        non-planar dislocations (like bcc screw) may also need a shift in
        the slip plane.  Cannot be given with shiftindex.  If neither shift
        nor shiftindex is given then shiftindex = 0 is used.
    shiftscale : bool, optional
        If False (default), a given shift value will be taken as absolute
        Cartesian.  If True, a given shift will be taken relative to the
        rotated cell's box vectors.
    tol : float
        A cutoff tolerance used with obtaining the dislocation solution.
        Only needs to be changed if there are issues with obtaining a
        solution.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. Default is 0.0.
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. Default is 0.0.
    maxiter : int, optional
        The maximum number of minimization iterations to use. Default is 
        10000.
    maxeval : int, optional
        The maximum number of minimization evaluations to use. Default is 
        100000.
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration. Default is
        0.01 Angstroms.
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. Default is 0.0,
        which will skip the dynamic relaxation.
    annealsteps : int, optional
        The number of time steps to run the dynamic relaxation for.  Default
        is None, which will run for 10000 steps if annealtemp is not 0.0.  
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed base system.
        - **'symbols_base'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the base system's
          atypes.
        - **'dumpfile_disl'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed dislocation dipole system.
        - **'symbols_disl'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the dislocation
          dipole system's atypes.
        - **'dislocation'** (*atomman.defect.Dislocation*) - The Dislocation
          object used to generate the dipole system.
        - **'E_total_disl'** (*float*) - The total potential energy of the
          dislocation dipole system.
    """
    # Construct dislocation configuration generator
    dislocation = am.defect.Dislocation(ucell, C, burgers, ξ_uvw, slip_hkl,
                                        m=m, n=n, tol=tol,
                                        conventional_setting=conventional_setting)
    
    # Generate the base and dislocation systems
    base_system, disl_system = dislocation.dipole(sizemults=sizemults,
                                                  shift=shift,
                                                  shiftindex=shiftindex,
                                                  shiftscale=shiftscale,
                                                  return_base_system=True)

    # Initialize results dict
    results_dict = {}

    # Save initial perfect system
    base_system.dump('atom_dump', f='base.dump')
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = base_system.symbols
    
    # Save dislocation generator
    results_dict['dislocation'] = dislocation

    # Relax system
    relaxed = disl_relax(lammps_command, disl_system, potential,
                         mpi_command=mpi_command, annealtemp=annealtemp,
                         annealsteps=annealsteps, randomseed=randomseed,
                         etol=etol, ftol=ftol, maxiter=maxiter, 
                         maxeval=maxeval, dmax=dmax)
    
    # Save relaxed dislocation system with original box vects
    system_disl = am.load('atom_dump', relaxed['dumpfile'], symbols=disl_system.symbols)
    
    system_disl.box_set(vects=disl_system.box.vects, origin=disl_system.box.origin)
    system_disl.dump('atom_dump', f='disl.dump')
    results_dict['dumpfile_disl'] = 'disl.dump'
    results_dict['symbols_disl'] = system_disl.symbols
    
    results_dict['E_total_disl'] = relaxed['E_total']
    
    # Cleanup files
    Path('0.dump').unlink()
    Path(relaxed['dumpfile']).unlink()
    for dumpjsonfile in Path('.').glob('*.dump.json'):
        dumpjsonfile.unlink()
    
    return results_dict

def disl_relax(lammps_command: str,
               system: am.System,
               potential: lmp.Potential,
               mpi_command: Optional[str] = None, 
               annealtemp: float = 0.0,
               annealsteps: Optional[int] = None,
               randomseed: Optional[int] = None,
               etol: float = 0.0,
               ftol: float = 1e-6,
               maxiter: int = 10000,
               maxeval: int = 100000,
               dmax: float = uc.set_in_units(0.01, 'angstrom')) -> dict:
    """
    Sets up and runs the disl_relax.in LAMMPS script for relaxing a
    dislocation monopole system.
    
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
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. Default is 0.0,
        which will skip the dynamic relaxation.
    annealsteps : int, optional
        The number of time steps to run the dynamic relaxation for.  Default
        is None, which will run for 10000 steps if annealtemp is not 0.0.        
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. Default is 0.0.
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. Default is 0.0.
    maxiter : int, optional
        The maximum number of minimization iterations to use default is 
        10000.
    maxeval : int, optional
        The maximum number of minimization evaluations to use default is 
        100000.
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration default is
        0.01 Angstroms.
        
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'logfile'** (*str*) - The name of the LAMMPS log file.
        - **'dumpfile'** (*str*) - The name of the LAMMPS dump file
          for the relaxed system.
        - **'E_total'** (*float*) - The total potential energy for the
          relaxed system.
    """
    if annealsteps is None:
        annealsteps = 10000
        
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    #lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='system.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['anneal_info'] = anneal_info(annealtemp, annealsteps, 
                                                  randomseed, potential.units)
    lammps_variables['dumpsteps'] = maxiter + annealsteps
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    
    # Write lammps input script
    lammps_script = 'disl_relax.in'
    template = read_calc_file('iprPy.calculation.dislocation_dipole',
                              'disl_relax.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command)
    thermo = output.simulations[-1]['thermo']
    
    # Extract output values
    results = {}
    results['logfile'] = 'log.lammps'
    results['dumpfile'] = '%i.dump' % thermo.Step.values[-1] 
    results['E_total'] = uc.set_in_units(thermo.PotEng.values[-1],
                                         lammps_units['energy'])
    
    return results

def anneal_info(temperature: float = 0.0,
                runsteps: Optional[int] = None,
                randomseed: Optional[int] = None,
                units: str = 'metal') -> str:
    """
    Generates LAMMPS commands for thermo anneal.
    
    Parameters
    ----------
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    units : str, optional
        The LAMMPS units style to use (default is 'metal').
    
    Returns
    -------
    str
        The generated LAMMPS input lines for performing a dynamic relax.
        Will be '' if temperature==0.0.
    """    
    # Return nothing if temperature is 0.0 (don't do thermo anneal)
    if temperature == 0.0:
        return ''
    
    # Generate velocity, fix nvt, and run LAMMPS command lines
    else:
        if randomseed is None:
            randomseed = random.randint(1, 900000000)
        if runsteps is None:
            runsteps = 10000
        
        start_temp = 2 * temperature
        tdamp = 100 * lmp.style.timestep(units)
        timestep = lmp.style.timestep(units)
        info = '\n'.join([
            'velocity all create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
            'fix nvt all nvt temp %f %f %f' % (temperature, temperature,
                                               tdamp),
            'timestep %f' % (timestep),
            'thermo %i' % (runsteps),
            'run %i' % (runsteps),
            ])
    
    return info
