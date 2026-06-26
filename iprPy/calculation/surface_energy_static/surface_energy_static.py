# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
import shutil
from typing import Optional, Union
from pathlib import Path

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps, millerindices
from atomman.lammps import LAMMPS, LAMMPSobj

def surface_energy_static(lammps_command: Union[str, LAMMPSobj],
                          ucell: am.System,
                          potential: lammpspotential,
                          hkl: millerindices,
                          mpi_command: Optional[str] = None,
                          sizemults: Union[list, tuple, None] = None,
                          minwidth: Optional[unitfloat] = None,
                          even: bool = False,
                          conventional_setting: str = 'p',
                          cutboxvector: str = 'c',
                          atomshift: Union[list, np.ndarray, None] = None,
                          shiftindex: Optional[int] = None,
                          etol: float = 0.0,
                          ftol: unitfloat = 0.0,
                          maxiter: int = 10000,
                          maxeval: int = 100000,
                          dmax: unitfloat = '0.01 angstrom',
                          usefiles: bool = False) -> dict:
    """
    Evaluates surface formation energies by slicing along one periodic
    boundary of a bulk system.
    
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
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed bulk system.
        - **'dumpfile_surf'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed system containing the free surfaces.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_surf'** (*float*) - The total potential energy of the
          relaxed system containing the free surfaces.
        - **'A_surf'** (*float*) - The area of the free surface.
        - **'E_pot'** (*float*) - The per-atom potential energy of the relaxed bulk
          system.
        - **'E_surf_f'** (*float*) - The computed surface formation energy.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    if minwidth is not None:
        minwidth = uc.set_in_units(minwidth)
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)

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
    system.wrap()

    # Evaluate system with free surface
    surf_results = min(lmp, system, etol=etol, ftol=ftol,
                       maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                       usefiles=usefiles)
    
    # Extract results from system with free surface
    dumpfile_surf = 'surface.dump'
    last_dump_file = f'{int(surf_results["Step"])}.dump'
    if Path(last_dump_file).is_file():
        shutil.move(last_dump_file, dumpfile_surf)
    else:
        surf_results['system_final'].dump('atom_dump', f=dumpfile_surf, float_format='%.17f')
    Epot_surf = surf_results['PotEng']

    # Evaluate perfect system (all pbc removes cut)
    system.pbc = [True, True, True]
    system.wrap()
    base_results = min(lmp, system, etol=etol, ftol=ftol,
                       maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                       usefiles=usefiles)
    
    # Extract results from perfect system
    dumpfile_base = 'perfect.dump'
    last_dump_file = f'{int(base_results["Step"])}.dump'
    if Path(last_dump_file).is_file():
        shutil.move(last_dump_file, dumpfile_base)
    else:
        base_results['system_final'].dump('atom_dump', f=dumpfile_base, float_format='%.17f')
    Epot_base = base_results['PotEng']
    
    # Clean up dump files
    if Path('0.dump').is_file():
        Path('0.dump').unlink()

    # Compute the free surface formation energy
    E_surf_f = (Epot_surf - Epot_base) / (2 * A_surf)
    
    # Save values to results dictionary
    results_dict = {}
    
    results_dict['dumpfile_base'] = dumpfile_base
    results_dict['dumpfile_surf'] = dumpfile_surf
    results_dict['E_total_base'] = Epot_base
    results_dict['E_total_surf'] = Epot_surf
    results_dict['A_surf'] = A_surf
    results_dict['E_pot'] = Epot_base / system.natoms
    results_dict['E_surf_f'] = E_surf_f
    
    return results_dict

def min(lmp: LAMMPSobj,
        system: am.System,
        etol: float = 0.0,
        ftol: float = 0.0,
        maxiter: int = 10000,
        maxeval: int = 100000,
        dmax: float = 0.01,
        logfile: str = 'none',
        usefiles: bool = False):

    """
    Performs an energy/force minimization calculation.
    
    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The atomic configuration to evaluate.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. Default is 0.0.
    ftol : float or str, optional
        The force tolerance for the structure minimization. This value is in
        units of force. Default is 0.0.
    maxiter : int, optional
        The maximum number of minimization iterations to use default is 
        10000.
    maxeval : int, optional
        The maximum number of minimization evaluations to use default is 
        100000.
    dmax : float or str, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration default is
        0.01 Angstroms.
    dump : bool, optional
        If True, the initial and final configurations will be saved as LAMMPS dump
        files.  Default value is False.
    return_system : bool, optional
        If True, the final relaxed configuration will be returned as an atomman.System
        object.
    tilt_large : bool, optional
        For LAMMPS versions prior to Dec 2022, a "box tilt large" command was needed if
        any box tilts exceed 50% of the reference box lengths.  Default value of False
        will never include the extra line.  Ignored if using a newer LAMMPS version.
    logfile : str or None, optional
        The file name to use for LAMMPS log files.  If None (default),
        no log file will be created.
    lammps_units : dict, optional
        Allows for passing in the units information associated with a LAMMPS
        units option if already known.  If not given, then atomman.lammps.style.unit()
        will be called using the unit setting for the potential.
    lammps_date : datetime.date, optional
        Allows for passing in the version date for the LAMMPS code being used.
        If not given, this will be obtained by calling atomman.lammps.versiondate().

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'PotEng'** (*float*) - The total potential energy of the system.
        - **'Lx'** (*float*) - The relaxed lx box length.
        - **'Ly'** (*float*) - The relaxed ly box length.
        - **'Lz'** (*float*) - The relaxed lz box length.
        - **'Xy'** (*float*) - The relaxed xy box tilt.
        - **'Xz'** (*float*) - The relaxed xz box tilt.
        - **'Yz'** (*float*) - The relaxed yz box tilt.
        - **'Pxx'** (*float*) - The measured xx component of the pressure on the system.
        - **'Pyy'** (*float*) - The measured yy component of the pressure on the system.
        - **'Pzz'** (*float*) - The measured zz component of the pressure on the system.
        - **'Pxy'** (*float*) - The measured xy component of the pressure on the system.
        - **'Pxz'** (*float*) - The measured xz component of the pressure on the system.
        - **'Pyz'** (*float*) - The measured yz component of the pressure on the system.
        - **'system_final'** (*atomman.System*) The relaxed system.  Only included if return_system is True.
    """
    if usefiles:
        logfile = logfile
        script = 'min.in'
    else:
        logfile = 'none'
        script = None

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)
    
    # Set up thermo info
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'xy', 'xz', 'yz',
                         'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'pe')
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