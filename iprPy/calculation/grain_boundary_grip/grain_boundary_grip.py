# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
import datetime
from pathlib import Path
from typing import Optional, Union
import secrets

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
import atomman.lammps as lmp
from atomman.tools import filltemplate
from atomman.defect import GrainBoundary, GRIP

# iprPy imports
from ...tools import read_calc_file

def grain_boundary_grip(lammps_command: str,
                        ucell: am.System,
                        potential: lmp.Potential,
                        uvws1: npt.ArrayLike,
                        uvws2: npt.ArrayLike,
                        potential_energy: float,
                        mpi_command: Optional[str] = None,
                        conventional_setting: str = 'p',
                        cutboxvector: str = 'c',
                        gbwidth: float = uc.set_in_units(10, 'angstrom'),
                        bufferwidth: float = uc.set_in_units(10, 'angstrom'),
                        boundarywidth: float = uc.set_in_units(10, 'angstrom'),
                        etol: float = 1e-15,
                        ftol: float = 1e-15,
                        maxiter: int = 100000,
                        maxeval: int = 1000000,
                        dmax: float = uc.set_in_units(0.01, 'angstrom'),
                        grip: Optional[GRIP] = None,
                        randomseed: Optional[int] = None,
                        verbose: bool = False,
                        **kwargs):
    """
    Creates a grain boundary using the GRIP algorithm, relaxes it using both
    MD integrations and minimization, and evaluates the grain boundary energy.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the grain boundary
        configurations.
    potential : atomman.lammps.Potential
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
    
    if randomseed is None: 
        randomseed = secrets.randbelow(2147483646)+1

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
    results = relax(lammps_command, system, potential,
                    grip.temperature, grip.runsteps,
                    mpi_command=mpi_command, gbwidth=gbwidth,
                    bufferwidth=bufferwidth, 
                    etol=etol, ftol=ftol, maxiter=maxiter,
                    maxeval=maxeval, dmax=dmax,
                    randomseed=randomseed)

    # Calculate grain boundary energy
    delta_pe = results['Epotgb'] - results['natomsgb'] * potential_energy
    gb_energy = delta_pe / A_fault

    results = {}
    results['grip'] = grip
    results['gb_energy'] = gb_energy
    results['dumpfile_final'] = 'final.dump'
    results['symbols_final'] = system.symbols
    
    return results

def relax(lammps_command: str,
          system: am.System,
          potential: lmp.Potential,
          temperature: float,
          runsteps: int,
          mpi_command: Optional[str] = None,
          gbwidth: float = uc.set_in_units(10, 'angstrom'),
          bufferwidth: float = uc.set_in_units(10, 'angstrom'),
          etol: float = 0.0,
          ftol: float = 0.0,
          maxiter: int = 10000,
          maxeval: int = 100000,
          dmax: float = uc.set_in_units(0.01, 'angstrom'),
          cutboxvector: str = 'c',
          randomseed: Optional[int] = None) -> dict:
    """
    Run a LAMMPS simulation in two steps: Optional high-temperature MD
    then relaxation. Writes the input structure with dummy GB energy
    if the LAMMPS executable path doesn't exist.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The grain boundary system to perform the relaxation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to relax the system at during the MD run.
    runsteps : int
        The number of MD run steps to perform.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
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
    assert cutboxvector == 'c', 'alt values not yet supported by relax()'

    # Get the units from Potential
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']

    # Random seed settings
    if randomseed is None: 
        randomseed = lmp.seed()

    # Use 2x the default timestep for the potential's units
    timestep = 2 * lmp.style.timestep(potential.units)
    
    # Define LAMMPS input script variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f=f'init.dat',
                                potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['temperature'] = temperature
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dmax'] = dmax
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] =  maxeval
    lammps_variables['gbwidth'] = uc.get_in_units(gbwidth, lammps_units['length'])
    lammps_variables['bufferwidth'] = uc.get_in_units(bufferwidth, lammps_units['length'])
    lammps_variables['randomseed'] = randomseed
    lammps_variables['timestep'] = timestep

    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'

    # Write LAMMPS input script
    lammps_script = 'grip_relax.in'
    template = read_calc_file('iprPy.calculation.grain_boundary_grip',
                                'grip_relax.template')
    with open(lammps_script, 'w') as f:
        f.write(am.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = am.lammps.run(lammps_command, script_name=lammps_script,   
                            mpi_command=mpi_command, screen=False)
    
    # Extract results
    thermo = output.simulations[-1].thermo
    
    # Rename final dump file
    Path(f'{thermo.Step.values[-1]}.dump').rename('final.dump')

    results = {}
    results['natomsgb'] = thermo.v_natomsgb.values[-1]
    results['Epotgb'] = uc.set_in_units(thermo.c_pegb.values[-1],
                                        lammps_units['energy'])

    return results