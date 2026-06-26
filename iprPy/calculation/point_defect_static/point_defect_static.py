# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps
from atomman.lammps import LAMMPS, LAMMPSobj

def point_defect_static(lammps_command: Union[str, LAMMPSobj],
                        system: am.System,
                        potential: lammpspotential,
                        point_kwargs: Union[list, dict],
                        cutoff: unitfloat,
                        mpi_command: Optional[str] = None,
                        etol: float = 0.0,
                        ftol: unitfloat = 0.0,
                        maxiter: int = 10000,
                        maxeval: int = 100000,
                        dmax: unitfloat = '0.01 angstrom',
                        tol: unitfloat = '1e-5 angstrom',
                        usefiles: bool = False) -> dict:
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy. Evaluates a relaxed system containing a point defect
    to determine if the defect structure has transformed to a different
    configuration.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float or str
        Cutoff distance to use in identifying neighbor atoms.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simulation in.  If not
        given, will use the current working directory.
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
    tol : float or str, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_pot'** (*float*) - The per-atom potential energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
          relaxed defect system.
        - **'pij_tensor'** (*numpy.ndarray of float*) - The elastic dipole
          tensor associated with the defect.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed defect system.
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
          has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.ndarray of float*) - The centrosummation
          parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.ndarray of float*) - The position_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.ndarray of float*) - The db_vect_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for dumbbell-style defects.
    """
    
    # Run ptd_energy to refine values
    results_dict = point_defect_relax(lammps_command,
                                      system,
                                      potential,
                                      point_kwargs,
                                      mpi_command = mpi_command,
                                      etol = etol,
                                      ftol = ftol,
                                      maxiter = maxiter,
                                      maxeval = maxeval,
                                      dmax = dmax,
                                      usefiles = usefiles)
    
    # Run check_ptd_config
    results_dict2 = check_ptd_config(results_dict['system_ptd'],
                                     point_kwargs,
                                     cutoff, tol)
    results_dict.update(results_dict2)

    return results_dict

def point_defect_relax(lammps_command: Union[str, LAMMPSobj],
                       system: am.System,
                       potential: lammpspotential,
                       point_kwargs: Union[list, dict],
                       mpi_command: Optional[str] = None,
                       etol: float = 0.0,
                       ftol: unitfloat = 0.0,
                       maxiter: int = 10000,
                       maxeval: int = 100000,
                       dmax: unitfloat = '0.01 angstrom',
                       usefiles: bool = False) -> dict:
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simulation in.  If not
        given, will use the current working directory.
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
        
        - **'E_pot'** (*float*) - The per-atom potential energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
          relaxed defect system.
        - **'pij_tensor'** (*numpy.ndarray of float*) - The elastic dipole
          tensor associated with the defect.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed defect system.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)
    
    # Relax base system with an energy/force minimization
    base_results = min(lmp, system, etol=etol, ftol=ftol,
                       maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                       usefiles=usefiles)
    
    
    # Extract energy and pressures of base
    Epot_base = base_results['PotEng']
    Epot_base_atom = Epot_base / system.natoms
    pxx = base_results['Pxx']
    pyy = base_results['Pyy']
    pzz = base_results['Pzz']
    pxy = base_results['Pxy']
    pxz = base_results['Pxz']
    pyz = base_results['Pyz']
    pressure_base = np.array([[pxx, pxy, pxz], [pxy, pyy, pyz], [pxz, pyz, pzz]])
    system_base = base_results['system_final']
    
    # Copy old box vectors if LAMMPS exe is used to minimize rounding
    if not lmp.islib:
        system_base.box_set(vects=system.box.vects)
    system_base.dump('atom_dump', f='perfect.dump', float_format='%.17f')
    
    # Add defect(s)
    system_ptd = deepcopy(system_base)
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        system_ptd = am.defect.point(system_ptd, **pkwargs)
    
    # Relax defect system with an energy/force minimization
    ptd_results = min(lmp, system_ptd, etol=etol, ftol=ftol,
                      maxiter=maxiter, maxeval=maxeval, dmax=dmax,
                      usefiles=usefiles)
    
    # Extract energy and pressures of ptd
    Epot_ptd = ptd_results['PotEng']
    pxx = ptd_results['Pxx']
    pyy = ptd_results['Pyy']
    pzz = ptd_results['Pzz']
    pxy = ptd_results['Pxy']
    pxz = ptd_results['Pxz']
    pyz = ptd_results['Pyz']
    pressure_ptd = np.array([[pxx, pxy, pxz], [pxy, pyy, pyz], [pxz, pyz, pzz]])
    system_ptd = ptd_results['system_final']
    
    # Copy old box vectors if LAMMPS exe is used to minimize rounding
    if not lmp.islib:
        system_ptd.box_set(vects=system.box.vects)
    system_ptd.dump('atom_dump', f='defect.dump', float_format='%.17f')
    
    # Compute defect formation energy
    E_ptd_f = Epot_ptd - Epot_base_atom * system_ptd.natoms
    
    # Compute strain tensor
    pij = -(pressure_base - pressure_ptd) * system_base.box.volume
    
    # Cleanup files
    for fname in Path.cwd().glob('atom.*'):
        fname.unlink()
    for dumpjsonfile in Path.cwd().glob('*.dump.json'):
        dumpjsonfile.unlink()
    
    # Return results
    results_dict = {}
    results_dict['E_pot'] = Epot_base_atom
    results_dict['E_ptd_f'] = E_ptd_f
    results_dict['E_total_base'] = Epot_base
    results_dict['E_total_ptd'] = Epot_ptd
    results_dict['pij_tensor'] = pij
    results_dict['system_base'] = system_base
    results_dict['system_ptd'] = system_ptd
    results_dict['dumpfile_base'] = 'perfect.dump'
    results_dict['dumpfile_ptd'] = 'defect.dump'
    
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

def check_ptd_config(system: am.System,
                     point_kwargs: Union[list, dict],
                     cutoff: unitfloat,
                     tol: unitfloat = '1e-5 angstrom') -> dict:
    """
    Evaluates a relaxed system containing a point defect to determine if the
    defect structure has transformed to a different configuration.
    
    Parameters
    ----------
    system : atomman.System
        The relaxed defect system.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float
        Cutoff distance to use in identifying neighbor atoms.
    tol : float, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
          has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.ndarray of float*) - The centrosummation
          parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.ndarray of float*) - The position_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.ndarray of float*) - The db_vect_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for dumbbell-style defects.
    """
    # Convert values given with units if needed
    cutoff = uc.set_in_units(cutoff)
    tol = uc.set_in_units(tol)

    # Check if point_kwargs is a list
    if not isinstance(point_kwargs, (list, tuple)):
        pos = point_kwargs['pos']
    
    # If it is a list of 1, use that set
    elif len(point_kwargs) == 1:
        point_kwargs = point_kwargs[0]
        pos = point_kwargs['pos']
        
    # If it is a list of two (divacancy), use the first and average position
    elif len(point_kwargs) == 2:
        pos = (np.array(point_kwargs[0]['pos'])
               + np.array(point_kwargs[1]['pos'])) / 2
        point_kwargs = point_kwargs[0]
    
    # More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')

    # Initially set has_reconfigured to False
    has_reconfigured = False
    
    # Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.pos, pos) 
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
                'centrosummation': centrosummation,
                'position_shift': position_shift}
        
    # Investigate if dumbbell vector has shifted direction 
    elif point_kwargs['ptd_type'] == 'db':
        db_vect = point_kwargs['db_vect'] / np.linalg.norm(point_kwargs['db_vect'])
        new_db_vect = system.dvect(-2, -1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation,
                'db_vect_shift': db_vect_shift}
    
    else:
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation}