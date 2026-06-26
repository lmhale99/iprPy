# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from pathlib import Path
from typing import Optional, Union
import shutil

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps, millerindices
from atomman.lammps import LAMMPS, LAMMPSobj

def stackingfaultmap(lammps_command: Union[str, LAMMPSobj],
                     ucell: am.System,
                     potential: lammpspotential,
                     hkl: millerindices,
                     mpi_command: Optional[str] = None,
                     sizemults: Union[list, tuple, None] = None,
                     minwidth: Optional[unitfloat] = None,
                     even: bool = False,
                     a1vect_uvw: Union[millerindices] = None,
                     a2vect_uvw: Union[millerindices] = None,
                     conventional_setting: str = 'p',
                     cutboxvector: str = 'c',
                     faultpos_rel: Optional[float] = None,
                     faultpos_cart: Optional[float] = None,
                     num_a1: int = 10,
                     num_a2: int = 10,
                     atomshift: Union[list, np.ndarray, None] = None,
                     shiftindex: Optional[int] = None,
                     etol: float = 0.0,
                     ftol: unitfloat = 0.0,
                     maxiter: int = 10000,
                     maxeval: int = 100000,
                     dmax: unitfloat = '0.01 angstrom',
                     usefiles: bool = False) -> dict:
    """
    Computes a generalized stacking fault map for shifts along a regular 2D
    grid.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the stacking fault
        configurations.
    potential : aPotentialLAMMPS or PotentialLAMMPSKIM
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
    num_a1 : int, optional
        The number of fractional coordinates to evaluate along a1vect_uvw.
        Default value is 10.
    num_a2 : int, optional
        The number of fractional coordinates to evaluate along a2vect_uvw.
        Default value is 10.
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
        
        - **'A_fault'** (*float*) - The area of the fault surface.
        - **'gamma'** (*atomman.defect.GammaSurface*) - A gamma surface
          plotting object.
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
    gsf_gen.surface(shift=atomshift, minwidth=minwidth, sizemults=sizemults,
                    even=even, faultpos_rel=faultpos_rel,
                    faultpos_cart=faultpos_cart)
    
    abovefault = gsf_gen.abovefault
    cutindex = gsf_gen.cutindex
    A_fault = gsf_gen.surfacearea

    # Define lists
    a1vals = []
    a2vals = []
    E_totals = []
    disps = []

    # Loop over all shift combinations
    for a1, a2, sfsystem in gsf_gen.iterfaultmap(num_a1=num_a1, num_a2=num_a2):
        a1vals.append(a1)
        a2vals.append(a2)

        # Evaluate the system at the shift
        tag = f'a{a1:.10f}-b{a2:.10f}'
        relax = stackingfaultrelax(lmp, sfsystem,
                                   cutboxvector=cutboxvector,
                                   etol=etol, ftol=ftol, maxiter=maxiter,
                                   maxeval=maxeval, dmax=dmax,
                                   logfile=f'{tag}-log.lammps', usefiles=usefiles)
        
        # Extract terms
        E_totals.append(relax['PotEng'])
        pos = relax['system_final'].atoms.pos
        disps.append(pos[abovefault, cutindex].mean()
                   - pos[~abovefault, cutindex].mean())
        dumpfile = f'{tag}.dump'
        last_dump_file = f'{int(relax["Step"])}.dump'
        if Path(last_dump_file).is_file():
            shutil.move(last_dump_file, dumpfile)
        else:
            relax['system_final'].dump('atom_dump', f=dumpfile, float_format='%.17f')
    
    # Clean up dump files
    if Path('0.dump').is_file():
        Path('0.dump').unlink()

    E_totals = np.array(E_totals)
    disps = np.array(disps)
    
    # Get zeroshift values
    E_total_0 = E_totals[0]
    disp_0 = disps[0]
    
    # Compute the stacking fault energies
    E_gsfs = (E_totals - E_total_0) / A_fault
    
    # Compute the change in displacement normal to fault plane
    delta_disps = disps - disp_0
    
    results_dict = {}
    results_dict['A_fault'] = A_fault
    results_dict['gamma'] = am.defect.GammaSurface(a1vect = gsf_gen.a1vect_uvw,
                                                   a2vect = gsf_gen.a2vect_uvw,
                                                   box = gsf_gen.ucell.box,
                                                   a1 = a1vals,
                                                   a2 = a2vals,
                                                   E_gsf = E_gsfs,
                                                   delta = delta_disps)

    return results_dict


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

