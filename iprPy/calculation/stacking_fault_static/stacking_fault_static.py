# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from pathlib import Path
import shutil
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps, millerindices
from atomman.lammps import LAMMPS, LAMMPSobj

def stackingfault(lammps_command: Union[str, LAMMPSobj],
                  ucell: am.System,
                  potential: lammpspotential,
                  hkl: millerindices,
                  mpi_command: Optional[str] = None,
                  sizemults: Union[list, tuple, None] = None,
                  minwidth: Optional[unitfloat] = None,
                  even: bool = False,
                  a1vect_uvw: Optional[millerindices] = None,
                  a2vect_uvw: Optional[millerindices] = None,
                  conventional_setting: str = 'p',
                  cutboxvector: str = 'c',
                  faultpos_rel: Optional[float] = None,
                  faultpos_cart: Optional[float] = None,
                  a1: float = 0.0,
                  a2: float = 0.0,
                  atomshift: Union[list, np.ndarray, None] = None,
                  shiftindex: Optional[int] = None,
                  etol: float = 0.0,
                  ftol: unitfloat = 0.0,
                  maxiter: int = 10000,
                  maxeval: int = 100000,
                  dmax: unitfloat = '0.01 angstrom',
                  usefiles: bool = False) -> dict:
    """
    Computes the generalized stacking fault value for a single faultshift.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the stacking fault
        configurations.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    hkl : array-like object or str
        The Miller(-Bravais) crystal fault plane relative to ucell.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sizemults : list or tuple, optional
        The three System.supersize multipliers [a_mult, b_mult, c_mult] to use on the
        rotated cell to build the final system. Note that the cutboxvector sizemult
        must be an integer and not a tuple.  Default value is [1, 1, 1].
    minwidth : float or str, optional
        If given, the sizemult along the cutboxvector will be selected such that the
        width of the resulting final system in that direction will be at least this
        value. If both sizemults and minwidth are given, then the larger of the two
        in the cutboxvector direction will be used. 
    even : bool, optional
        A True value means that the sizemult for cutboxvector will be made an even
        number by adding 1 if it is odd.  Default value is False.
    a1vect_uvw : array-like object or str, optional
        The crystal vector to use for one of the two shifting vectors.  If
        not given, will be set to the shortest in-plane lattice vector.
    a2vect_uvw : array-like object or str, optional
        The crystal vector to use for one of the two shifting vectors.  If
        not given, will be set to the shortest in-plane lattice vector not
        parallel to a1vect_uvw.
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
    faultpos_rel : float, optional
        The position to place the slip plane within the system given as a
        relative coordinate along the out-of-plane direction.  faultpos_rel
        and faultpos_cart cannot both be given.  Default value is 0.5 if 
        faultpos_cart is also not given.
    faultpos_cart : float, optional
        The position to place the slip plane within the system given as a
        Cartesian coordinate along the out-of-plane direction.  faultpos_rel
        and faultpos_cart cannot both be given.
    a1 : float, optional
        The fractional coordinate to evaluate along a1vect_uvw.
        Default value is 0.0.
    a2 : float, optional
        The fractional coordinate to evaluate along a2vect_uvw.
        Default value is 0.0.
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
    ftol : float or str, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float or str, optional
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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    if minwidth is not None:
        minwidth = uc.set_in_units(minwidth)
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)

    # Construct stacking fault configuration generator
    gsf_gen = am.defect.StackingFault(hkl, ucell, cutboxvector=cutboxvector,
                                      a1vect_uvw=a1vect_uvw, a2vect_uvw=a2vect_uvw,
                                      conventional_setting=conventional_setting)
    
    # Check shift parameters
    if shiftindex is not None:
        assert atomshift is None, 'shiftindex and atomshift cannot both be given'
        atomshift = gsf_gen.shifts[shiftindex]
    elif atomshift is None:
        atomshift = gsf_gen.shifts[0]

    # Generate the free surface (zero-shift) configuration
    sfsystem = gsf_gen.surface(shift=atomshift, minwidth=minwidth,
                               sizemults=sizemults, even=even,
                               faultpos_rel=faultpos_rel,
                               faultpos_cart=faultpos_cart)

    abovefault = gsf_gen.abovefault
    cutindex = gsf_gen.cutindex
    A_fault = gsf_gen.surfacearea

    # Evaluate the zero shift configuration
    zeroshift = stackingfaultrelax(lmp, sfsystem,
                                   cutboxvector=cutboxvector,
                                   etol=etol, ftol=ftol, maxiter=maxiter,
                                   maxeval=maxeval, dmax=dmax,
                                   logfile='zeroshift-log.lammps', usefiles=usefiles)
    
    # Extract results from zero shift
    dumpfile_zero = 'zeroshift.dump'
    last_dump_file = f'{int(zeroshift["Step"])}.dump'
    if Path(last_dump_file).is_file():
        shutil.move(last_dump_file, dumpfile_zero)
    else:
        zeroshift['system_final'].dump('atom_dump', f=dumpfile_zero, float_format='%.17f')
    E_total_0 = zeroshift['PotEng']
    pos_0 = zeroshift['system_final'].atoms.pos

    # Evaluate the system after shifting along the fault plane
    sfsystem = gsf_gen.fault(a1=a1, a2=a2)
    shifted = stackingfaultrelax(lmp, sfsystem,
                                 cutboxvector=cutboxvector,
                                 etol=etol, ftol=ftol, maxiter=maxiter,
                                 maxeval=maxeval, dmax=dmax,
                                 logfile='shifted-log.lammps', usefiles=usefiles)
    
    # Extract results from the shifted system
    dumpfile_shifted = 'shifted.dump'
    last_dump_file = f'{int(shifted["Step"])}.dump'
    if Path(last_dump_file).is_file():
        shutil.move(last_dump_file, dumpfile_shifted)
    else:
        shifted['system_final'].dump('atom_dump', f=dumpfile_shifted, float_format='%.17f')
    E_total_sf = shifted['PotEng']
    pos_sf = shifted['system_final'].atoms.pos

    # Clean up dump files
    if Path('0.dump').is_file():
        Path('0.dump').unlink()

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


def stackingfaultrelax(lmp: LAMMPSobj,
                       system: am.System,
                       cutboxvector: str = 'c',
                       etol: float = 0.0,
                       ftol: float = 0.0,
                       maxiter: int = 10000,
                       maxeval: int = 100000,
                       dmax: float = 0.01,
                       logfile: str = 'none',
                       usefiles: bool = False) -> dict:
    """
    Perform a stacking fault relaxation simulation for a single fault shift.
    
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
    if usefiles:
        logfile = logfile
        script = 'sfmin.in'
    else:
        logfile = 'none'
        script = None

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)
    
    # Give correct LAMMPS fix setforce command
    if cutboxvector == 'a':
        lmp.cmd.fix('cut', 'all', 'setforce', 'NULL', 0, 0)
    elif cutboxvector == 'b':
        lmp.cmd.fix('cut', 'all', 'setforce', 0, 'NULL', 0)
    elif cutboxvector == 'c':
        lmp.cmd.fix('cut', 'all', 'setforce', 0, 0, 'NULL')
    else: 
        raise ValueError('Invalid cutboxvector')
    
    # Set up thermo info
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'pxx', 'pyy', 'pzz', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Define compute for per atom potential energy
    lmp.cmd.compute('peatom', 'all', 'pe/atom')

    # Create dump file if needed/requested
    if usefiles or not lmp.islib:
        if lmp.potential.atom_style == 'charge':
            dumpkeys = ['id', 'type', 'q', 'x', 'y', 'z', 'c_peatom']
        else:
            dumpkeys = ['id', 'type', 'x', 'y', 'z', 'c_peatom']
        lmp.cmd.dump('dumpit', 'all', 'custom', maxiter, '*.dump', *dumpkeys)
        lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')

    # Minimization settings and run
    lmp.cmd.min_modify('dmax', uc.get_in_units(dmax, lmp.unitsdict['length']))
    lmp.cmd.minimize(etol, uc.get_in_units(ftol, lmp.unitsdict['force']), maxiter, maxeval)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    if log is None:
        # Get thermo directly from lammps object if no log file
        thermo: dict = lmp.last_thermo()
    else:
        # Extract thermo terms from log output
        thermo = log.simulations[-1].thermo.iloc[-1].to_dict()

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)

    if usefiles or not lmp.islib:
        # Read final system from dump file
        final_dump = f'{int(thermo["Step"])}.dump'
        system_final = am.load('atom_dump', final_dump, symbols=system.symbols,
                               lammps_units=lmp.potential.units)

    else:
        # Load final system information directly from LAMMPS
        system_final = am.load('lammps_lib', lmp, symbols=system.symbols,
                               lammps_units=lmp.potential.units)
        if lmp.potential.atom_style == 'charge':
            charge = lmp.numpy.extract_atom('q', nelem=system.natoms, dim=1)
            system_final.atoms.charge = charge
        system_final.atoms.c_peatom = lmp.numpy.extract_compute('peatom', lammps.LMP_STYLE_ATOM, lammps.LMP_TYPE_VECTOR)
    
    # Unit conversion of system_final atom properties
    system_final.atoms.c_peatom = uc.set_in_units(system_final.atoms.c_peatom, lmp.unitsdict['energy'])
    if 'charge' in system_final.atoms_prop():
        system_final.atoms.charge = uc.set_in_units(system_final.atoms.charge, lmp.unitsdict['charge'])

    thermo['system_final'] = system_final
    return thermo

