# Python script created by Lucas Hale

# Standard library imports
import shutil
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps
from atomman.lammps import LAMMPS, LAMMPSobj

def relax_static(lammps_command: Union[str, LAMMPSobj],
                 system: am.System,
                 potential: lammpspotential,
                 mpi_command: Optional[str] = None,
                 pxx: unitfloat = 0.0,
                 pyy: unitfloat = 0.0,
                 pzz: unitfloat = 0.0,
                 pxy: unitfloat = 0.0,
                 pxz: unitfloat = 0.0,
                 pyz: unitfloat = 0.0,
                 dispmult: float = 0.0,
                 etol: float = 0.0,
                 ftol: unitfloat = 0.0,
                 maxiter: int = 100000,
                 maxeval: int = 1000000,
                 dmax: unitfloat = '0.01 angstrom',
                 maxcycles: int = 100,
                 ctol: float = 1e-10,
                 raise_at_maxcycles: bool = False,
                 usefiles: bool = False) -> dict:
    """
    Repeatedly runs the ELASTIC example distributed with LAMMPS until box
    dimensions converge within a tolerance.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    pxx : float or str, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    pyy : float or str, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    pzz : float or str, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    pxy : float or str, optional
        The value to relax the xy shear pressure component to (default is
        0.0).
    pxz : float or str, optional
        The value to relax the xz shear pressure component to (default is
        0.0).
    pyz : float or str, optional
        The value to relax the yz shear pressure component to (default is
        0.0).
    dispmult : float, optional
        Multiplier for applying a random displacement to all atomic positions
        prior to relaxing. Default value is 0.0.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    pressure_unit : str, optional
        The unit of pressure to calculate the elastic constants in (default is
        'GPa').
    maxcycles : int, optional
        The maximum number of times the minimization algorithm is called.
        Default value is 100.
    ctol : float, optional
        The relative tolerance used to determine if the lattice constants have
        converged (default is 1e-10).
    raise_at_maxcycles : bool, optional
        Setting this to True will raise an error if maxcycles is reached before
        achieving convergence within ctol.  When False, the final relaxed
        configuration is retained even without achieving the ctol.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_initial'** (*str*) - The name of the initial dump file
          created.
        - **'symbols_initial'** (*list*) - The symbols associated with the
          initial dump file.
        - **'dumpfile_final'** (*str*) - The name of the final dump file
          created.
        - **'symbols_final'** (*list*) - The symbols associated with the final
          dump file.
        - **'lx'** (*float*) - The relaxed lx box length.
        - **'ly'** (*float*) - The relaxed ly box length.
        - **'lz'** (*float*) - The relaxed lz box length.
        - **'xy'** (*float*) - The relaxed xy box tilt.
        - **'xz'** (*float*) - The relaxed xz box tilt.
        - **'yz'** (*float*) - The relaxed yz box tilt.
        - **'E_pot'** (*float*) - The potential energy per atom for the final
          configuration.
        - **'measured_pxx'** (*float*) - The measured x tensile pressure
          component for the final configuration.
        - **'measured_pyy'** (*float*) - The measured y tensile pressure
          component for the final configuration.
        - **'measured_pzz'** (*float*) - The measured z tensile pressure
          component for the final configuration.
        - **'measured_pxy'** (*float*) - The measured xy shear pressure
          component for the final configuration.
        - **'measured_pxz'** (*float*) - The measured xz shear pressure
          component for the final configuration.
        - **'measured_pyz'** (*float*) - The measured yz shear pressure
          component for the final configuration.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pxx = uc.set_in_units(pxx)
    pyy = uc.set_in_units(pyy)
    pzz = uc.set_in_units(pzz)
    pxy = uc.set_in_units(pxy)
    pxz = uc.set_in_units(pxz)
    pyz = uc.set_in_units(pyz)
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)
    
    # Save initial configuration as a dump file
    system.dump('atom_dump', f='initial.dump')
    
    # Apply small random distortions to atoms
    system.atoms.pos += dispmult * np.random.rand(*system.atoms.pos.shape) - dispmult / 2
    
    # Initialize parameters
    old_vects = system.box.vects
    converged = False
    
    # Run minimizations up to maxcycles times
    for cycle in range(maxcycles):
        logfile = f'log-{cycle}.lammps'
        min_results = minbox(lmp, system,
                             pxx=pxx, pyy=pyy, pzz=pzz,
                             pxy=pxy, pxz=pxz, pyz=pyz,
                             etol=etol, ftol=ftol, maxiter=maxiter,
                             maxeval=maxeval, dmax=dmax, logfile=logfile,
                             usefiles=usefiles)
        
        # Clean up dump files
        if Path('0.dump').is_file():
            Path('0.dump').unlink()
        last_dump_file = f'{int(min_results["Step"])}.dump'
        if Path(last_dump_file).is_file():
            renamed_dump_file = f'relax_static-{cycle}.dump'
            shutil.move(last_dump_file, renamed_dump_file)
        
        # Update system
        system = min_results['system_final']
        
        # Test if box dimensions have converged
        if np.allclose(old_vects, system.box.vects, rtol=ctol, atol=0):
            converged = True
            break
        else:
            old_vects = system.box.vects
    
    # Check for convergence
    if converged is False and raise_at_maxcycles is True:
        raise RuntimeError('Failed to converge after ' + str(maxcycles) + ' cycles')
    
    # Zero out near-zero tilt factors
    lx = system.box.lx
    ly = system.box.ly
    lz = system.box.lz
    xy = system.box.xy
    xz = system.box.xz
    yz = system.box.yz
    if np.isclose(xy/ly, 0.0, rtol=0.0, atol=1e-10):
        xy = 0.0
    if np.isclose(xz/lz, 0.0, rtol=0.0, atol=1e-10):
        xz = 0.0
    if np.isclose(yz/lz, 0.0, rtol=0.0, atol=1e-10):
        yz = 0.0
    system.box.set(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)
    system.wrap()

    # Save final configuration as a dump file
    system.dump('atom_dump', f='final.dump')
    
    # Build results_dict
    results_dict = {}
    results_dict['dumpfile_initial'] = 'initial.dump'
    results_dict['symbols_initial'] = system.symbols
    results_dict['dumpfile_final'] = 'final.dump'
    results_dict['symbols_final'] = system.symbols
    results_dict['E_pot'] = min_results['PotEng'] / system.natoms
    
    results_dict['lx'] = lx
    results_dict['ly'] = ly
    results_dict['lz'] = lz
    results_dict['xy'] = xy
    results_dict['xz'] = xz
    results_dict['yz'] = yz
    
    results_dict['measured_pxx'] = min_results['Pxx']
    results_dict['measured_pyy'] = min_results['Pyy']
    results_dict['measured_pzz'] = min_results['Pzz']
    results_dict['measured_pxy'] = min_results['Pxy']
    results_dict['measured_pxz'] = min_results['Pxz']
    results_dict['measured_pyz'] = min_results['Pyz']
    
    return results_dict


def minbox(lmp: LAMMPSobj,
           system: am.System,
           pxx: float = 0.0,
           pyy: float = 0.0,
           pzz: float = 0.0,
           pxy: float = 0.0,
           pxz: float = 0.0,
           pyz: float = 0.0,
           etol: float = 0.0,
           ftol: float = 0.0,
           maxiter: int = 10000,
           maxeval: int = 100000,
           dmax: float = 0.01,
           logfile: str = 'none',
           usefiles: bool = False):

    """
    Performs an energy/force minimization calculation with box relax.
    
    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The atomic configuration to evaluate.
    pxx : float or str, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    pyy : float or str, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    pzz : float or str, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    pxy : float or str, optional
        The value to relax the xy shear pressure component to (default is
        0.0).
    pxz : float or str, optional
        The value to relax the xz shear pressure component to (default is
        0.0).
    pyz : float or str, optional
        The value to relax the yz shear pressure component to (default is
        0.0).
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
        script = 'minbox.in'
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
    lmp.cmd.fix('boxrelax', 'all', 'box/relax', 'x', pxx, 'y', pyy, 'z', pzz, 'xy', pxy, 'xz', pxz, 'yz', pyz)
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
