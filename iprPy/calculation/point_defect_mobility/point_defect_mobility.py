# Python script created by Jacob Hechter and Lucas Hale

# Standard library imports
from typing import Optional, Union
from copy import deepcopy
from pathlib import Path
import shlex
import shutil

# http://www.numpy.org/
import numpy as np 
import numpy.typing as npt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def point_defect_mobility(lammps_command: Union[str, LAMMPSobj],
                          system: am.System,
                          potential: lammpspotential,
                          neb_pos1: npt.ArrayLike,
                          neb_pos2: npt.ArrayLike,
                          mpi_command: Optional[str] = None,
                          neb_symbol: Union[str, list, None] = None,
                          numreplicas: int = 11,
                          partition: Optional[str] = None,
                          point_kwargs: Union[list, dict, None] = None,
                          etol: float = 0.0,
                          ftol: unitfloat = 0.0,
                          dmax: unitfloat = '0.01 angstrom',
                          springconst: unitfloat = '5 eV/angstrom^2',
                          thermosteps: int = 100,
                          dumpsteps: Optional[int] = None,
                          minsteps: int = 10000,
                          climbsteps: int = 10000,
                          usefiles: bool = False):
    """
    Evaluates the mobility of point defects using NEB.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on consisting of the atoms that
        are not to be subjected to the NEB forces.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    neb_pos1: array-like
        The position(s) of the atom(s) in the initial replica that are to be
        subjected to the NEB interaction forces.
    neb_pos2: array-like
        The position(s) of the atom(s) in the initial replica that are to be
        subjected to the NEB interaction forces.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    neb_symbol: str, list, or None, optional
        The potential symbol model to assign to each of the NEB atoms.  Value(s)
        are required unless all atoms of system are the same, in which the
        symbol(s) for the NEB atom(s) are inferred to also be the same.
    numreplicas : int, optional
        The number of NEB replicas to use.  Default value is 11.
    partition: str or None, optional
        The value for the LAMMPS command line partition option that should be
        of the form 'MxN' where M is the number of partitions (replicas) and
        N is the number of cores per replica.  If not given, this will default
        to M=numreplicas and N=1. 
    point_kwargs : dict, list of dict, or None, optional
        Any dictionaries containing the keyword arguments for the
        atomman.defect.point() function to modify the system with to alter the
        set of non-NEB atoms.   
    etol : float, optional
        The energy tolerance for the NEB  algorithm. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the NEB algorithm. This value is in
        units of force. (Default is 0.0).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    springconst : float, optional
        The NEB spring constant value to use.  Default value is 5.
    thermosteps : int, optional
        How often to output thermo data to the log.lammps files.  This is
        mostly useful for NEB runs to check convergence progress.  Default
        value is 100.
    dumpsteps : int or None, optional
        How often to generate dump configuration files for the replicas.
        Default value of None will set this to the max of (minsteps, climbsteps)
        so that only three states will be dumped: the initial unrelaxed, and the
        relaxed states at the end of the two NEB operations. 
    minsteps : int, optional
        The maximum number of steps to perform during the NEB minimization
        operation.  Default value is 10000.
    climbsteps : int, optional
        The maximum number of steps to perform during the NEB climbing
        operation.  Default value is 10000.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
      
        - **'neb_coordinates'** (*numpy.ndarray*) - The final NEB reaction
          coordinates for each replica after both min and climb operations.
        - **'neb_energies'** (*numpy.ndarray*) - The final energies for
          each replica after both min and climb operations.
        - **'neb_positions'** (*numpy.ndarray*) - The final positions
          of each NEB atom in each replica after both min and climb operations.
        - **'forward_barrier'** (*float*) - The energy barrier for the forward
          reaction: difference between max energy and the first replica's energy.
        - **'reverse_barrier'** (*float*) - The energy barrier for the reverse
          reaction: difference between max energy and the last replica's energy.
    """
    # Build the partition option for the LAMMPS command
    if partition is None:
        partition = f'{numreplicas}x1'
    
    # Create a LAMMPS object if needed
    if isinstance(lammps_command, str) and shutil.which(shlex.split(lammps_command)[0]) is None:
        cmdargs = ['-l', 'none', '-screen', 'none', '-partition', partition]
    else:
        cmdargs = None
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, cmdargs=cmdargs,
                 potential=potential)

    # Convert values given with units if needed
    ftol = float(uc.set_in_units(ftol))
    dmax = float(uc.set_in_units(dmax))
    springconst = float(uc.set_in_units(springconst))

    # First check of pos values
    neb_pos1 = np.asarray(neb_pos1)
    if neb_pos1.shape == (3,):
        neb_pos1 = neb_pos1.reshape(1,3)
    if neb_pos1.ndim != 2 or neb_pos1.shape[1] != 3:
        raise ValueError('neb_pos1 must be an array of shape (3,) or (N,3)')

    neb_pos2 = np.asarray(neb_pos2)
    if neb_pos2.shape == (3,):
        neb_pos2 = neb_pos2.reshape(1,3)
    if neb_pos2.ndim != 2 or neb_pos2.shape[1] != 3:
        raise ValueError('neb_pos2 must be an array of shape (3,) or (N,3)')
    
    if neb_pos1.shape[0] != neb_pos2.shape[0]:
        raise ValueError('neb_pos1 and neb_pos2 must be the same length')

    # Safe copy system into firstsystem
    firstsystem = deepcopy(system)

    # Add point defect(s) to initial system if needed
    if point_kwargs is not None:
        if not isinstance(point_kwargs, (list, tuple)):
            point_kwargs = [point_kwargs]
        for pkwargs in point_kwargs:
            firstsystem = am.defect.point(firstsystem, **pkwargs)

    # Check symbols for the mobile atoms(s)
    if neb_symbol is None:
        if len(firstsystem.symbols) == 1:
            neb_symbol = firstsystem.symbols[0]
        else:
            raise ValueError('system has multiple atypes so symbol(s) must be specified for mobile atoms')
    if isinstance(neb_symbol, str):
        symbol = neb_symbol
        neb_symbol = [symbol for i in range(neb_pos1.shape[0])]
    elif len(neb_symbol) != neb_pos1.shape[0]:
        raise ValueError('neb_symbol not the same length as neb_pos1')
    
    # Match symbols and atypes
    atype = []
    symbols = list(firstsystem.symbols)
    for symbol in neb_symbol:
        if symbol not in symbols:
            symbols.append(symbol)
        atype.append(symbols.index(symbol) + 1)

    # Figure out atom ids for the mobile atoms
    min_a_id = firstsystem.natoms 
    max_a_id = min_a_id + neb_pos1.shape[0]
    a_ids = [i for i in range(min_a_id, max_a_id)]

    # Build Atoms objects for the mobile atoms
    atoms1 = am.Atoms(atype=atype, pos=neb_pos1)
    atoms2 = am.Atoms(atype=atype, pos=neb_pos2, a_id=a_ids)

    # Modify/build systems
    firstsystem = firstsystem.atoms_extend(atoms1, symbols=symbols)
    lastsystem = am.System(atoms=atoms2, box=firstsystem.box)
            
    # Run NEB
    neblog = neb(lmp, firstsystem, lastsystem, partition=partition,
                 id_key='a_id', id_start0=True,
                 etol=etol, ftol=ftol, dmax=dmax, numreplicas=numreplicas,
                 springconst=springconst, thermosteps=thermosteps,
                 dumpsteps=dumpsteps, minsteps=minsteps,
                 climbsteps=climbsteps, usefiles=usefiles)

    # Get final step and NEB path values at that step
    finalstep = neblog.climbrun.Step.values[-1]
    coord, energy = neblog.get_neb_path(finalstep)
    
    # Add final path and barrier 
    results = {}
    results['neb_coordinates'] = coord
    results['neb_energies'] = energy

    # Get the moving atom positions for each replica
    moving_pos = np.empty((len(a_ids), numreplicas, 3))
    for r in range(numreplicas):
        replica = am.load('atom_dump', f'step-{finalstep}.replica-{r+1}.dump')
        for i, a_id in enumerate(a_ids):
            moving_pos[i, r, :] = replica.atoms.pos[a_id, :]
    results['neb_positions'] = moving_pos

    # Add barrier energies
    results['forward_barrier'] = neblog.get_barrier()
    results['reverse_barrier'] = neblog.get_barrier(reverse=True)

    return results

def neb(lmp: LAMMPSobj,
        firstsystem: am.System,
        lastsystem: am.System,
        numreplicas: int,
        partition: str,
        id_key: Optional[str] = None,
        id_start0: bool = True,
        etol: float = 0.0,
        ftol: float = 0.0,
        dmax: float = 0.01,
        springconst: float = 5, 
        thermosteps: int = 100,
        dumpsteps: Optional[int] = None, 
        minsteps: int = 10000,
        climbsteps: int = 10000,
        usefiles: bool = False) -> dict:
    """
    Sets up and runs the neb.template LAMMPS script for performing an NEB
    calculation between two configurations.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    firstsystem : atomman.System
        The system configuration corresponding to the first replica.  This
        should be a full system that defines the box and all atoms.
    lastsystem : atomman.System
        The system configuration corresponding to the final replica.  No
        box information is used, and only the atoms to subject to NEB forces
        need to be included.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    numreplicas : int, optional
        The number of NEB replicas to use.  Default value is 11.
    partition: str or None, optional
        The value for the LAMMPS command line partition option that should be
        of the form 'MxN' where M is the number of partitions (replicas) and
        N is the number of cores per replica.  If not given, this will default
        to M=numreplicas and N=1. 
    id_key : str or None, optional
        The name of the atoms property of lastsystem to match the contained
        NEB atoms to those in firstsystem.  A default value of None will use
        the atom array indices meaning that either all atoms need to be in
        lastsystem or that the first atom(s) in firstsystem are the NEB atoms.
    id_start0 : bool, optional
        A value of True (default) indicates that the id_key values are relative
        to an array that starts at 0 as in the case of atomman atom indices.  A
        value of False indicates that the id_key values are relative to an array
        that starts at 1 as in the case of the LAMMPS atom id values.
    etol : float, optional
        The energy tolerance for the NEB  algorithm. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the NEB algorithm. This value is in
        units of force. (Default is 0.0).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    springconst : float, optional
        The NEB spring constant value to use.  Default value is 5.
    thermosteps : int, optional
        How often to output thermo data to the log.lammps files.  This is
        mostly useful for NEB runs to check convergence progress.  Default
        value is 100.
    dumpsteps : int or None, optional
        How often to generate dump configuration files for the replicas.
        Default value of None will set this to the max of (minsteps, climbsteps)
        so that only three states will be dumped: the initial unrelaxed, and the
        relaxed states at the end of the two NEB operations. 
    minsteps : int, optional
        The maximum number of steps to perform during the NEB minimization
        operation.  Default value is 10000.
    climbsteps : int, optional
        The maximum number of steps to perform during the NEB climbing
        operation.  Default value is 10000.

    Returns
    -------
    atomman.lammps.NEBLog
        The collection of all thermo and NEB data from within all of the
        log.lammps values for both individual replicas and the overall NEB
        run.
    """
    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'neb_lammps.in'
    else:
        script = None

    # Set default dumpsteps
    if dumpsteps is None:
        dumpsteps = max(minsteps, climbsteps)

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)

    lmp.commands_string('# LAMMPS setting parameters')
    lmp.cmd.clear()
    lmp.cmd.atom_modify('map', 'array')

    # Pass systems and potential info into LAMMPS
    lmp.new_system_from_data_file(firstsystem, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile, clear=False)
    lastsystem.dump('neb_replica', f='final.dat',
                     id_key=id_key, id_start0=id_start0)

    lmp.commands_string('# property compute definitions')
    lmp.cmd.compute('peatom', 'all', 'pe/atom')

    lmp.commands_string('# define neb')
    springconst_units = f'{lmp.unitsdict['force']}/{lmp.unitsdict['length']}'
    lmp.cmd.fix('neb', 'all', 'neb', uc.set_in_units(springconst, springconst_units))

    lmp.commands_string('# dump file definition')
    lmp.cmd.variable('i', 'uloop', numreplicas)
    lmp.cmd.dump('dumpy', 'all', 'custom', dumpsteps, 'step-*.replica-${i}.dump',
                 'id', 'type', 'x', 'y', 'z', 'c_peatom')
    lmp.cmd.dump_modify('dumpy', 'format', 'float', '%.17e')

    lmp.commands_string('# thermo definition')
    lmp.cmd.thermo(thermosteps)
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    lmp.commands_string('# minimization definition')
    lmp.cmd.timestep(timestep)
    lmp.cmd.min_style('quickmin')
    lmp.cmd.min_modify('dmax', uc.get_in_units(dmax, lmp.unitsdict['length']))

    lmp.commands_string('# run neb')
    lmp.cmd.neb(etol, uc.get_in_units(ftol, lmp.unitsdict['force']),
                minsteps, climbsteps, thermosteps, 'final', 'final.dat')

    # Run EXE, get log output
    log = lmp.end_and_get_log(script, partition=partition)

    # Read and return NEB log output
    neblog = am.lammps.NEBLog()

    return neblog
