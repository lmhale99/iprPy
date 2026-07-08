# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps
from atomman.lammps import LAMMPS, LAMMPSobj

def grain_boundary_static(lammps_command: Union[str, LAMMPSobj],
                          ucell: am.System,
                          potential: lammpspotential,
                          uvws1: npt.ArrayLike,
                          uvws2: npt.ArrayLike,
                          potential_energy: unitfloat,
                          mpi_command: Optional[str] = None,
                          conventional_setting: str = 'p',
                          cutboxvector: str = 'c',
                          gbwidth: unitfloat = '20 angstrom',
                          boundarywidth: unitfloat = '10 angstrom',
                          num_a1: int = 8,
                          num_a2: int = 8,
                          deletefrom: str = 'top',
                          min_deleter = 0.30,
                          max_deleter = 0.99,
                          num_deleter = 100,
                          etol: float = 1e-15,
                          ftol: unitfloat = '1e-15 eV/atom',
                          maxiter: int = 100000,
                          maxeval: int = 1000000,
                          dmax: unitfloat = '0.01 angstrom',
                          alldump: bool = True,
                          usefiles: bool = False) -> dict:
    """
    Evaluates the energy of a grain boundary by building a two grain system and
    statically relaxing a range of atomic configurations that iterate over
    planar shifts and inter-planar atomic deletion.

    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the grain boundary
        configurations.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    uvws1 : array-like object
        The Miller(-Bravais) crystal vectors associated with rotating ucell to
        form the 'top' grain.
    uvws2 : array-like object
        The Miller(-Bravais) crystal vectors associated with rotating ucell to
        form the 'bottom' grain.
    potential_energy : float, optional
        The per-atom potential energy of the bulk crystal to use for the grain
        boundary energy calculation.  This is currently limited to a single
        value so it only works with elemental systems.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', is
        out-of-plane with the grain boundary (default is 'c').
    conventional_setting : str, optional
        Specifies the cell setting for ucell if it is a non-primitive unit cell.
        This is used in generating the boundary configuration and determining
        the smallest out-of-plane lattice vector component.
    gbwidth : float, optional
        The width of the region around the grain boundary that will be relaxed.
        Note that the region itself will be twice as thick as gbwidth as it is
        applied to both crystals independently.  Default value is 20 angstroms.
    boundarywidth : float, optional
        The minimum width of the boundary region beyond the gbwidth where
        atoms exist but are not subjected to relaxation. This region prevents
        the other atoms from seeing a free surface.  Default value is 10
        angstroms.
    num_a1 : int, optional
        The number of in-plane shifts to perform in one of the two in-plane
        directions.  Default value is 8.
    num_a2 : int, optional
        The number of in-plane shifts to perform in one of the two in-plane
        directions.  Default value is 8.
    min_deleter : float, optional
        The minimum interatomic distance to use for identifying atoms to delete
        based on being within this distance from other atoms across the grain
        boundary.  Values are taken as relative to the ucell's r0.  Default
        value is 0.3.
    max_deleter : float, optional
        The maximum interatomic distance to use for identifying atoms to delete
        based on being within this distance from other atoms across the grain
        boundary.  Values are taken as relative to the ucell's r0.  Default
        value is 0.99.
    num_deleter : int, optional
        The number of interatomic distances to use for identifying atoms to
        delete based on being close to others across the grain boundary.  Note
        that only unique configurations will be relaxed, so this value sets
        the max number of configurations per a1,a2 shift that will be explored
        through atom deletion.  Default value is 100.
    deletefrom : str, optional
        Indicates which of the two grains 'top' or 'bottom' that the close
        boundary atoms are to be deleted from.  A value of 'both' will
        independently iterate over both top and bottom deletions.  Default
        value is 'top'.
    conventional_setting : str, optional
        Allows for rotations of a primitive unit cell to be determined from
        (hkl) indices specified relative to a conventional unit cell.  Allowed
        settings: 'p' for primitive (no conversion), 'f' for face-centered,
        'i' for body-centered, and 'a', 'b', or 'c' for side-centered.  Default
        behavior is to perform no conversion, i.e. take (hkl) relative to the
        given ucell.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 1e-15).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 1e-15).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        100000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        1000000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'gb_energies'** (*list*) - The grain boundary energies computed for
          all configurations iterated over.
        - **'min_gb_energy'** (*float*) - The minimum grain boundary energy.
        - **'final_dump'** (*str*) - The name of the atom dump file that
          corresponds to the min_gb_energy.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    potential_energy = float(uc.set_in_units(potential_energy))
    gbwidth = float(uc.set_in_units(gbwidth))
    boundarywidth = float(uc.set_in_units(boundarywidth))
    ftol = float(uc.set_in_units(ftol))
    dmax = float(uc.set_in_units(dmax))

    gb = am.defect.GrainBoundary(ucell, uvws1, uvws2,
                                 conventional_setting=conventional_setting,
                                 cutboxvector=cutboxvector)
    
    # Add boundary width and identify multiples
    minwidth = gbwidth + boundarywidth
    gb.identifymults(minwidth=minwidth, setvalues=True)

    # Build list of deleter values
    deleters = np.linspace(min_deleter, max_deleter, num_deleter) * ucell.r0()
    
    i = 0
    gb_energies = []
    A_fault = None
    min_gb_energy = np.inf
    min_i = -1
    for system, natoms1 in gb.iterboundaryshift(deletefrom=deletefrom,
                                                shifts1=num_a1, shifts2=num_a2,
                                                freesurface=True, 
                                                deleters=deleters):
        
        # Cut out excess atoms to save calc time
        keepids = np.where(
            (system.atoms.pos[:, gb.cutindex] > -minwidth) &
            (system.atoms.pos[:, gb.cutindex] <  minwidth))
        system = system.atoms_ix[keepids]

        # Compute grain boundary area for first configuration (same for all)
        if i == 0:
            if cutboxvector == 'a':
                A_fault = np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
            elif cutboxvector == 'b':
                A_fault = np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
            elif cutboxvector == 'c':
                A_fault = np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
            else:
                raise ValueError("cutboxvector limited to values 'a', 'b', or 'c'")

        # Relax the configuration
        results = grain_boundary_relax(lmp,
                                       system,
                                       gbwidth=gbwidth,
                                       etol = etol,
                                       ftol = ftol,
                                       maxiter = maxiter,
                                       maxeval = maxeval,
                                       gbindex = i,
                                       cutboxvector = cutboxvector,
                                       dmax = dmax,
                                       usefiles = usefiles)
        
        # Calculate grain boundary energy
        delta_pe = results['Epotgb'] - results['natomsgb'] * potential_energy
        gb_energy = delta_pe / A_fault
        
        # Check if energy is < current minimum
        if gb_energy < min_gb_energy:
            min_gb_energy = gb_energy
            if not alldump and min_i != -1:
                # Delete previous lowest energy structure
                Path(f'{min_i}.dump').unlink()
            min_i = i
        
        elif not alldump:
            # Delete dump file if not the lowest energy structure
            Path(f'{i}.dump').unlink()

        # Append energy to the list and increase i
        gb_energies.append(gb_energy)
        i += 1
    
    results = {}
    results['gb_energies'] = gb_energies
    results['min_gb_energy'] = min_gb_energy
    results['dumpfile_final'] = f'{min_i}.dump'
    results['symbols_final'] = system.symbols
    
    return results

def grain_boundary_relax(lmp: LAMMPSobj,
                         system: am.System,
                         gbwidth: float = 20.0,
                         etol: float = 0.0,
                         ftol: float = 0.0,
                         maxiter: int = 10000,
                         maxeval: int = 100000,
                         dmax: float = 0.01,
                         cutboxvector = 'c', 
                         gbindex: int = 0,
                         usefiles: bool = False) -> dict:
    """
    Sets up and runs an energy/force minimization using LAMMPS for a single
    grain boundary configuration.

    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The grain boundary system to perform the relaxation on.
    gbwidth : float, optional
        The width of the region around the grain boundary that will be relaxed.
        Note that the region itself will be twice as thick as gbwidth as it is
        applied to both crystals independently.  Default value is 20 angstroms.
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
    cutboxvector : str, optional
        Indicates which box vector of the system is not in the grain boundary
        plane.  This is used to determine which Cartesian axes direction the
        system is allowed to relax.  Default value is 'c'.
    gbindex : int, optional
        Integer index label for the configuration. This is used to uniquely
        name the LAMMPS log file and the final relaxed dump file for every
        iterated plane shift and atom deletion.  Default value is 0.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'gbindex'** (*int*) - The index label used.
        - **'natoms'** (*int*) - The number of atoms in the configuration.
        - **'potentialenergy'** (*float*) - The total potential energy of
          the relaxed system.
    """
    # Handle file generation settings
    if usefiles:
        logfile = 'log.lammps'
        script = 'gbmin.in'
    else:
        logfile = 'none'
        script = None
    
    lmp.commands_string('\n# Define relaxation region width')
    lmp.cmd.variable('gbwidth', 'equal', uc.get_in_units(gbwidth, lmp.unitsdict['length']))

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)
    
    lmp.commands_string('\n# Define regions')
    if cutboxvector == 'a':
        lmp.cmd.region('relax', 'block', '-${gbwidth}', '${gbwidth}', 'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topboundary', 'block', '${gbwidth}', 'INF', 'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF', '-${gbwidth}', 'INF', 'INF', 'INF', 'INF', 'units', 'box')
    elif cutboxvector == 'b':
        lmp.cmd.region('relax', 'block', 'INF', 'INF', '-${gbwidth}', '${gbwidth}', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topboundary', 'block', 'INF', 'INF', '${gbwidth}', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF', 'INF', 'INF', '-${gbwidth}', 'INF', 'INF', 'units', 'box')
    elif cutboxvector == 'c':
        lmp.cmd.region('relax', 'block', 'INF', 'INF', 'INF', 'INF', '-${gbwidth}', '${gbwidth}', 'units', 'box')
        lmp.cmd.region('topboundary', 'block', 'INF', 'INF', 'INF', 'INF', '${gbwidth}', 'INF', 'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF', 'INF', 'INF', 'INF', 'INF', '-${gbwidth}', 'units', 'box')
    else:
        raise ValueError("cutboxvector limited to values 'a', 'b', or 'c'")

    lmp.commands_string('\n# Define region groups')
    lmp.cmd.group('relax', 'region', 'relax')
    lmp.cmd.group('topboundary', 'region', 'topboundary')
    lmp.cmd.group('botboundary', 'region', 'botboundary')

    lmp.commands_string('\n# Define property computes')
    lmp.cmd.compute('peatom', 'all', 'pe/atom')
    lmp.cmd.compute('pegb', 'relax', 'reduce', 'sum', 'c_peatom')
    lmp.cmd.variable('natomsgb', 'equal', 'count(relax)')

    lmp.commands_string('\n# Define thermo style')
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz',
                         'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz',
                         'c_pegb', 'v_natomsgb')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Create dump file if needed/requested
    if usefiles or not lmp.islib:
        lmp.commands_string('\n# Define dump')
        if lmp.potential.atom_style == 'charge':
            dumpkeys = ['id', 'type', 'q', 'x', 'y', 'z', 'c_peatom']
        else:
            dumpkeys = ['id', 'type', 'x', 'y', 'z', 'c_peatom']
        lmp.cmd.dump('dumpit', 'all', 'custom', maxiter, 'run_*.dump', *dumpkeys)
        lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')
    
    lmp.commands_string('\n# Set up and run minimization')
    lmp.cmd.fix('bothold', 'botboundary', 'setforce', 0.0, 0.0, 0.0)
    lmp.cmd.fix('tophold', 'topboundary', 'aveforce', 0.0, 0.0, 0.0)
    lmp.cmd.min_style('cg')
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
    
    # Save/rename final dump
    dumpfile = f'{gbindex}.dump'
    if usefiles or not lmp.islib:
        # Rename final dump file if it exists
        Path(f'run_{int(thermo["Step"])}.dump').rename(dumpfile)
        for atomfile in Path('.').glob('run_*.dump'):
            atomfile.unlink()

    else:
        # Load final system information directly from LAMMPS
        system_final = am.load('lammps_lib', lmp, symbols=system.symbols,
                               lammps_units=lmp.potential.units)
        if lmp.potential.atom_style == 'charge':
            charge = lmp.numpy.extract_atom('q', nelem=system.natoms, dim=1)
            system_final.atoms.charge = charge
        system_final.atoms.c_peatom = lmp.numpy.extract_compute('peatom', lammps.LMP_STYLE_ATOM, lammps.LMP_TYPE_VECTOR)
        system_final.dump('atom_dump', f=dumpfile, float_format='%.17e')
    
    results = {}
    results['gbindex'] = gbindex
    results['natomsgb'] = thermo['v_natomsgb']
    results['Epotgb'] = uc.set_in_units(thermo['c_pegb'],
                                        lmp.unitsdict['energy'])
    
    return results

