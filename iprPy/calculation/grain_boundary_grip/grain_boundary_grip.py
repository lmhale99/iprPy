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
from atomman.defect import GrainBoundary, GRIP

def grain_boundary_grip(lammps_command: Union[str, LAMMPSobj],
                        ucell: am.System,
                        potential: lammpspotential,
                        uvws1: npt.ArrayLike,
                        uvws2: npt.ArrayLike,
                        potential_energy: float,
                        mpi_command: Optional[str] = None,
                        conventional_setting: str = 'p',
                        cutboxvector: str = 'c',
                        gbwidth: unitfloat = '10 angstrom',
                        bufferwidth: unitfloat = '10 angstrom',
                        boundarywidth: unitfloat = '10 angstrom',
                        etol: float = 1e-15,
                        ftol: unitfloat = '1e-15 eV/atom',
                        maxiter: int = 100000,
                        maxeval: int = 1000000,
                        dmax: unitfloat = '0.01 angstrom',
                        grip: Optional[GRIP] = None,
                        randomseed: Optional[int] = None,
                        verbose: bool = False,
                        usefiles: bool = False,
                        **kwargs):
    """
    Creates a grain boundary using the GRIP algorithm, relaxes it using both
    MD integrations and minimization, and evaluates the grain boundary energy.

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
    conventional_setting : str, optional
        Specifies the cell setting for ucell if it is a non-primitive unit cell.
        This is used in generating the boundary configuration and determining
        the smallest out-of-plane lattice vector component.
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', is
        out-of-plane with the grain boundary (default is 'c').  
    gbwidth : float, optional
        The width of the grain boundary region taken as the distance into both
        crystals from the grain boundary plane.  This region will be relaxed
        during both the MD and minimization stages.  Note that the region
        itself will be twice as thick as gbwidth as it is applied to both
        crystals independently.  Default value is 10 angstroms.
    bufferwidth : float, optional
        The width of the buffer regions that separate the grain boundary
        region from the fixed atom surface boundary regions.  The buffer
        regions will not be relaxed during the MD stage, but will be relaxed
        during the minimization stage. Default value is 10 angstroms.
    boundarywidth : float, optional
        The minimum width of the boundary region beyond both gbwidth and
        bufferwidth where atoms exist but are not subjected to relaxations.
        This region prevents the other atoms from seeing a free surface.
        Default value is 10 angstroms.
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
    grip : atomman.defect.GRIP, optional
        A pre-defined GRIP object that collects and manages the parameters of
        the GRIP grain boundary generation algorithm.  If not given, a new GRIP
        object will be created from the default settings and **kwargs.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities.  Only used
        if resetvelocities is True.  Default is None which will select a
        random int between 1 and 900000000.
    verbose : bool, optional
        Setting this to True will print GRIP algorithm data for the run.
    **kwargs : any, optional
        If grip is not given, then any additional kwargs given will be used to
        initialize a new GRIP object.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'grip'** (*atomman.defect.GRIP*) - A GRIP object containing all
          the parameters used and generated by the GRIP algorithm.
        - **'gb_energy'** (*float*) - The grain boundary energy computed for
          the relaxed configuration.
        - **'dumpfile_final'** (*str*) - The atom dump file of the final relaxed
          configuration.
        - **'symbols_final'** (*str*) - The atomic model symbols associated with
          dumpfile_final.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    potential_energy = float(uc.set_in_units(potential_energy))
    gbwidth = float(uc.set_in_units(gbwidth))
    bufferwidth = float(uc.set_in_units(bufferwidth))
    boundarywidth = float(uc.set_in_units(boundarywidth))
    ftol = float(uc.set_in_units(ftol))
    dmax = float(uc.set_in_units(dmax))

    # Set randomseed
    randomseed = am.lammps.seed(randomseed)

    # Build grip parameters if needed
    if grip is None:
        grip = GRIP(**kwargs)
    elif len(kwargs) > 0:
        print(kwargs)
        raise ValueError('no kwargs can be given with grip')
    
    # Update/set GRIP minwidth
    grip.minwidth = gbwidth + bufferwidth + boundarywidth

    # Build grain boundary builder
    gb = GrainBoundary(ucell, uvws1, uvws2,
                       conventional_setting=conventional_setting,
                       cutboxvector=cutboxvector)
    
    # Generate grain boundary system
    system = grip.boundary(gb, randomseed=randomseed, verbose=verbose)[0]
    
    # Cut out excess atoms to save calc time
    keepids = np.where(
        (system.atoms.pos[:, gb.cutindex] > -grip.minwidth) &
        (system.atoms.pos[:, gb.cutindex] <  grip.minwidth))
    system = system.atoms_ix[keepids]

    # Compute grain boundary area
    if cutboxvector == 'a':
        A_fault = np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
    elif cutboxvector == 'b':
        A_fault = np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
    elif cutboxvector == 'c':
        A_fault = np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
    else:
        raise ValueError("cutboxvector limited to values 'a', 'b', or 'c'")

    # Relax the configuration
    results = grip_relax(lmp, system, grip.temperature, grip.runsteps,
                         gbwidth=gbwidth,
                         bufferwidth=bufferwidth, 
                         etol=etol, ftol=ftol, maxiter=maxiter,
                         maxeval=maxeval, dmax=dmax,
                         randomseed=randomseed, usefiles=usefiles)

    # Calculate grain boundary energy
    delta_pe = results['Epotgb'] - results['natomsgb'] * potential_energy
    gb_energy = delta_pe / A_fault

    results = {}
    results['grip'] = grip
    results['gb_energy'] = gb_energy
    results['dumpfile_final'] = 'final.dump'
    results['symbols_final'] = system.symbols
    
    return results

def grip_relax(lmp: LAMMPSobj,
               system: am.System,
               temperature: float,
               runsteps: int,
               coolsteps: int = 1000,
               temperature_low: float = 50,
               gbwidth: float = 10,
               bufferwidth: float = 10,
               etol: float = 0.0,
               ftol: float = 0.0,
               maxiter: int = 10000,
               maxeval: int = 100000,
               dmax: float = 0.01,
               cutboxvector: str = 'c',
               randomseed: Optional[int] = None,
               usefiles: bool = False) -> dict:
    """
    Run a LAMMPS simulation in two steps: Optional high-temperature MD
    then relaxation. Writes the input structure with dummy GB energy
    if the LAMMPS executable path doesn't exist.

    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The grain boundary system to perform the relaxation on.
    temperature : float
        The temperature to relax the system at during the MD run.
    runsteps : int
        The number of MD run steps to perform.
    coolsteps : int, optional
        The number of MD run steps to perform when cooling from temperature
        down to near zero.  Default value is 1000.
    temperature_low : float, optional
        The final target temperature of the cooling stage.  Default value is
        50.
    gbwidth : float, optional
        The width of the grain boundary region taken as the distance into both
        crystals from the grain boundary plane.  This region will be relaxed
        during both the MD and minimization stages.  Note that the region
        itself will be twice as thick as gbwidth as it is applied to both
        crystals independently.  Default value is 10 angstroms.
    bufferwidth : float, optional
        The width of the buffer regions that separate the grain boundary
        region from the fixed atom surface boundary regions.  The buffer
        regions will not be relaxed during the MD stage, but will be relaxed
        during the minimization stage. Default value is 10 angstroms.
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
    cutboxvector : str, optional
        Indicates which box vector of the system is not in the grain boundary
        plane.  This is used to determine which Cartesian axes direction the
        system is allowed to relax.  Default value is 'c'.
    randomseed : int or None, optional
        Random number seed used by LAMMPS.  Default is None which will select
        a random int between 1 and 2147483647.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'natomsgb'** (*int*) - The number of atoms in the grain boundary
          region.
        - **'Epotgb'** (*float*) - The total potential energy of
          the grain boundary region after relaxing.
    """
    # Handle file generation settings
    if usefiles:
        logfile = 'log.lammps'
        script = 'grip_relax.in'
    else:
        logfile = 'none'
        script = None

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep
    
    lmp.commands_string('\n# Define region widths')
    lmp.cmd.variable('gbwidth', 'equal', uc.get_in_units(gbwidth, lmp.unitsdict['length']))
    lmp.cmd.variable('bufferwidth', 'equal', uc.get_in_units(bufferwidth, lmp.unitsdict['length']))
    lmp.cmd.variable('energybufferwidth', 'equal', uc.get_in_units(1.5, lmp.unitsdict['length']))
    lmp.cmd.variable('gbbufferwidth', 'equal', '${gbwidth}+${bufferwidth}')
    lmp.cmd.variable('energywidth', 'equal', '${gbbufferwidth}+${energybufferwidth}')

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('\n# Define regions')
    if cutboxvector == 'a':
        lmp.cmd.region('gbregion',    'block', '-${gbwidth}',       '${gbwidth}',       'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topbuffer',   'block', '${gbwidth}',        '${gbbufferwidth}', 'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botbuffer',   'block', '-${gbbufferwidth}', '-${gbwidth}',      'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topboundary', 'block', '${gbbufferwidth}',  'INF',              'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF',               '-${gbwidth}',      'INF', 'INF', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('energyeval',  'block', '-${energywidth}',   '${energywidth}',   'INF', 'INF', 'INF', 'INF', 'units', 'box')
    elif cutboxvector == 'b':
        lmp.cmd.region('gbregion',    'block', 'INF', 'INF', '-${gbwidth}',       '${gbwidth}',        'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topbuffer',   'block', 'INF', 'INF', '${gbwidth}',        '${gbbufferwidth}',  'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botbuffer',   'block', 'INF', 'INF', '-${gbbufferwidth}', '-${gbwidth}',       'INF', 'INF', 'units', 'box')
        lmp.cmd.region('topboundary', 'block', 'INF', 'INF', '${gbbufferwidth}',  'INF',               'INF', 'INF', 'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF', 'INF', 'INF',               '-${gbbufferwidth}', 'INF', 'INF', 'units', 'box')
        lmp.cmd.region('energyeval',  'block', 'INF', 'INF', '-${energywidth}',   '${energywidth}',    'INF', 'INF', 'units', 'box')
    elif cutboxvector == 'c':
        lmp.cmd.region('gbregion',    'block', 'INF', 'INF', 'INF', 'INF', '-${gbwidth}',       '${gbwidth}',        'units', 'box')
        lmp.cmd.region('topbuffer',   'block', 'INF', 'INF', 'INF', 'INF', '${gbwidth}',        '${gbbufferwidth}',  'units', 'box')
        lmp.cmd.region('botbuffer',   'block', 'INF', 'INF', 'INF', 'INF', '-${gbbufferwidth}', '-${gbwidth}',       'units', 'box')
        lmp.cmd.region('topboundary', 'block', 'INF', 'INF', 'INF', 'INF', '${gbbufferwidth}',  'INF',               'units', 'box')
        lmp.cmd.region('botboundary', 'block', 'INF', 'INF', 'INF', 'INF', 'INF',               '-${gbbufferwidth}', 'units', 'box')
        lmp.cmd.region('energyeval',  'block', 'INF', 'INF', 'INF', 'INF', '-${energywidth}',   '${energywidth}',    'units', 'box')
    else:
        raise ValueError("cutboxvector limited to values 'a', 'b', or 'c'")

    lmp.commands_string('\n# Define region groups')
    lmp.cmd.group('gbregion', 'region', 'gbregion')
    lmp.cmd.group('topbuffer', 'region', 'topbuffer')
    lmp.cmd.group('botbuffer', 'region', 'botbuffer')
    lmp.cmd.group('topboundary', 'region', 'topboundary')
    lmp.cmd.group('botboundary', 'region', 'botboundary')
    lmp.cmd.group('energyeval', 'region', 'energyeval')

    lmp.commands_string('\n# Define composite groups')
    lmp.cmd.group('topboundary_md', 'union', 'topbuffer', 'topboundary')
    lmp.cmd.group('botboundary_md', 'union', 'botbuffer', 'botboundary')
    lmp.cmd.group('gbregion_min', 'union', 'gbregion', 'topbuffer', 'botbuffer')

    # Check if MD relaxation should be performed
    if runsteps > 0 and temperature > 0:

        lmp.commands_string('\n# Fix atoms in buffer and boundary regions')
        lmp.cmd.fix('bothold', 'botboundary_md', 'setforce', 0.0, 0.0, 0.0)
        lmp.cmd.fix('tophold', 'topboundary_md', 'aveforce', 0.0, 0.0, 0.0)

        lmp.commands_string('\n# Minimize')
        lmp.cmd.min_style('cg')
        lmp.cmd.min_modify('dmax', uc.get_in_units(dmax, lmp.unitsdict['length']))
        lmp.cmd.minimize(etol, uc.get_in_units(ftol, lmp.unitsdict['force']), maxiter, maxeval)

        lmp.commands_string('\n# Set timestep and initialize velocities')
        lmp.cmd.timestep(timestep)
        lmp.cmd.velocity('gbregion', 'create', 2*temperature, randomseed,
                         'dist', 'gaussian', 'rot', 'yes')

        lmp.commands_string('\n# MD relaxation')
        lmp.cmd.fix('nve', 'all', 'nve')
        lmp.cmd.fix('langevin', 'gbregion', 'langevin',
                    temperature, temperature, temperature_damp, randomseed)
        lmp.cmd.run(runsteps)

        lmp.commands_string('\n# Cool the system')
        lmp.cmd.unfix('langevin')
        lmp.cmd.fix('langevin', 'gbregion', 'langevin',
                    temperature, temperature_low, temperature_damp, randomseed)
        lmp.cmd.run(coolsteps)

        lmp.commands_string('\n# Unfix everything')
        lmp.cmd.unfix('bothold')
        lmp.cmd.unfix('tophold')
        lmp.cmd.unfix('langevin')
        lmp.cmd.unfix('nve')
        lmp.cmd.reset_timestep(0)

    lmp.commands_string('\n# Define property computes')
    lmp.cmd.compute('peatom', 'all', 'pe/atom')
    lmp.cmd.compute('pegb', 'energyeval', 'reduce', 'sum', 'c_peatom')
    lmp.cmd.variable('natomsgb', 'equal', 'count(energyeval)')

    lmp.commands_string('\n# Define thermo')
    lmp.cmd.thermo(0)
    lmp.cmd.thermo_style('custom', 'step', 'pe', 'lx', 'ly', 'lz', 'press', 'pxx', 'pyy', 'pzz', 'c_pegb', 'v_natomsgb')
    
    lmp.commands_string('\n# Define dump')
    if lmp.potential.atom_style == 'charge':
        dumpkeys = ['id', 'type', 'q', 'x', 'y', 'z', 'c_peatom']
    else:
        dumpkeys = ['id', 'type', 'x', 'y', 'z', 'c_peatom']
    lmp.cmd.dump('dumpit', 'all', 'custom', maxiter, '*.dump', *dumpkeys)
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

    # Rename final dump file
    Path(f'{int(thermo["Step"])}.dump').rename('final.dump')

    results = {}
    results['natomsgb'] = thermo['v_natomsgb']
    results['Epotgb'] = uc.set_in_units(thermo['c_pegb'],
                                        lmp.unitsdict['energy'])

    return results