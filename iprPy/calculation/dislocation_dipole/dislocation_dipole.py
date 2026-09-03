# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, millerindices, lammps
from atomman.lammps import LAMMPS, LAMMPSobj

def dislocation_dipole(lammps_command: Union[str, LAMMPSobj],
                       ucell: am.System,
                       potential: lammpspotential,
                       C: am.ElasticConstants,
                       burgers: millerindices,
                       ξ_uvw: millerindices,
                       slip_hkl: millerindices,
                       mpi_command: Optional[str] = None,
                       m: Union[list, np.ndarray] = [0,1,0],
                       n: Union[list, np.ndarray] = [0,0,1],
                       conventional_setting: str = 'p',
                       sizemults = None,
                       shift: Union[list, np.ndarray, None] = None,
                       shiftscale: bool = False,
                       shiftindex: Optional[int] = None,
                       tol: float = 1e-8,
                       etol: float = 0.0,
                       ftol: unitfloat = 0.0,
                       maxiter: int = 10000,
                       maxeval: int = 100000,
                       dmax: unitfloat = '0.01 angstrom',
                       annealtemp: float = 0.0,
                       annealsteps: Optional[int] = None,
                       randomseed: Optional[int] = None,
                       usefiles: bool = False) -> dict:
    """
    Creates and relaxes a dislocation dipole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The unit cell to use as the seed for generating the dislocation
        monopole system.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
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
    if usefiles:
        logfile = 'log.lammps'
        script = 'disl_relax.in'
    else:
        logfile = 'none'
        script = None
    
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)

    # Set randomseed
    randomseed = am.lammps.seed(randomseed)

    if annealsteps is None:
        if annealtemp > 0.0:
            annealsteps = 10000
        else:
            annealsteps = 0

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

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(disl_system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    # Define dump and thermo output information
    lmp.cmd.compute('peatom', 'all', 'pe/atom')
    lmp.cmd.dump('first', 'all', 'custom', maxiter + annealsteps, '*.dump',
                 'id', 'type', 'x', 'y', 'z', 'c_peatom')
    lmp.cmd.dump_modify('first', 'format', 'float', '%.17e')
    lmp.cmd.thermo_style('custom', 'step', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Perform an optional dynamic relaxation
    if annealtemp > 0.0 and annealsteps > 0:
        start_temp = 2 * annealtemp
        timestep = am.lammps.style.timestep(lmp.potential.units)
        temperature_damp = 100 * timestep
        
        lmp.cmd.velocity('all', 'create', start_temp, randomseed,
                         'mom', 'yes', 'rot', 'yes', 'dist', 'gaussian')
        lmp.cmd.fix('nvt', 'all', 'nvt', 'temp', annealtemp, annealtemp, temperature_damp)
        lmp.cmd.timestep(timestep)
        lmp.cmd.thermo(annealsteps)
        lmp.cmd.run(annealsteps)

    # Perform energy/force minimization
    lmp.cmd.min_modify('dmax', uc.get_in_units(dmax, lmp.unitsdict['length']))
    lmp.cmd.minimize(etol, uc.get_in_units(ftol, lmp.unitsdict['force']), maxiter, maxeval)

    # Run EXE versions, get log output
    log = lmp.end_and_get_log(script)

    if log is None:
        # Get thermo directly from lammps object if no log file
        thermo: dict = lmp.last_thermo()
    else:
        # Extract thermo terms from log output
        thermo = log.simulations[-1].thermo.iloc[-1].to_dict()

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)

    final_dump = f'{int(thermo["Step"])}.dump'
    if usefiles or not lmp.islib:
        # Read final system from dump file
        system_final = am.load('atom_dump', final_dump, symbols=disl_system.symbols,
                               lammps_units=lmp.potential.units)

    else:
        # Load final system information directly from LAMMPS
        system_final = am.load('lammps_lib', lmp, symbols=disl_system.symbols,
                               lammps_units=lmp.potential.units)
        if lmp.potential.atom_style == 'charge':
            charge = lmp.numpy.extract_atom('q', nelem=disl_system.natoms, dim=1)
            system_final.atoms.charge = charge
        system_final.atoms.c_peatom = lmp.numpy.extract_compute('peatom', lammps.LMP_STYLE_ATOM, lammps.LMP_TYPE_VECTOR)
    
    system_final.box_set(vects=disl_system.box.vects, origin=disl_system.box.origin)
    system_final.dump('atom_dump', f='disl.dump')
    
    
    # Initialize results dict
    results_dict = {}

    # Save initial perfect system
    base_system.dump('atom_dump', f='base.dump')
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = base_system.symbols
    
    # Save dislocation generator
    results_dict['dislocation'] = dislocation
    
    results_dict['dumpfile_disl'] = 'disl.dump'
    results_dict['symbols_disl'] = system_final.symbols
    
    results_dict['E_total_disl'] = thermo['PotEng']
    
    # Cleanup files
    Path('0.dump').unlink()
    Path(final_dump).unlink()
    
    return results_dict
