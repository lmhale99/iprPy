# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
import datetime
from pathlib import Path
from typing import Optional

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
import atomman.lammps as lmp
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def grain_boundary_static(lammps_command: str,
                          ucell: am.System,
                          potential: lmp.Potential,
                          uvws1: npt.ArrayLike,
                          uvws2: npt.ArrayLike,
                          mpi_command: Optional[str] = None,
                          conventional_setting: str = 'p',
                          cutboxvector: str = 'c',
                          minwidth: float = 0.0,
                          num_a1: int = 8,
                          num_a2: int = 8,
                          deletefrom: str = 'top',
                          min_deleter = 0.30,
                          max_deleter = 0.99,
                          num_deleter = 100,
                          potential_energy: float = 0.0,
                          etol: float = 0.0,
                          ftol: float = 0.0,
                          maxiter: int = 10000,
                          maxeval: int = 100000,
                          dmax: float = uc.set_in_units(0.01, 'angstrom')):
    """
    Evaluates the energy of a grain boundary by building a two grain system and
    statically relaxing a range of atomic configurations that iterate over
    planar shifts and inter-planar atomic deletion.

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
    minwidth : float, optional
        The minimum width to use for the system along the cutboxvector.  Default
        value is 0.0, which will use the un-multiplied uvw crystal vectors
        along this direction.
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
    potential_energy : float, optional
        The per-atom potential energy of the bulk crystal to use for the grain
        boundary energy calculation.  This is currently limited to a single
        value so it only works with elemental systems.  Default value is 0.0. 
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

    lammps_date = lmp.checkversion(lammps_command)['date']

    gb = am.defect.GrainBoundary(ucell, uvws1, uvws2,
                       conventional_setting=conventional_setting,
                       cutboxvector=cutboxvector)
    gb.identifymults(minwidth=minwidth, setvalues=True)

    # Build list of deleter values
    deleters = np.linspace(min_deleter, max_deleter, num_deleter) * ucell.r0()
    
    
    i = 0
    gb_energies = []
    A_fault = None
    for system, natoms1 in gb.iterboundaryshift(deletefrom=deletefrom,
                                                shifts1=num_a1, shifts2=num_a2,
                                                deleters=deleters):
        
        # Compute grain boundary area for first configuration (same for all)
        if i == 0:
            if cutboxvector == 'a':
                A_fault = 2 * np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
            elif cutboxvector == 'b':
                A_fault = 2 * np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
            elif cutboxvector == 'c':
                A_fault = 2 * np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
            else:
                raise ValueError("cutboxvector limited to values 'a', 'b', or 'c'")

        # Relax the configuration
        results = grain_boundary_relax(lammps_command,
                                       system,
                                       potential,
                                       mpi_command=mpi_command,
                                       etol = etol,
                                       ftol = ftol,
                                       lammps_date=lammps_date,
                                       maxiter = maxiter,
                                       maxeval = maxeval,
                                       gbindex = i,
                                       cutboxvector = cutboxvector,
                                       dmax = dmax)
        i += 1
 
        # Calculate grain boundary energy
        total_pe = results['potentialenergy']
        delta_pe = total_pe - system.natoms * potential_energy
        gb_energy = delta_pe / A_fault
        
        gb_energies.append(gb_energy)
    
    min_gb_energy = min(gb_energies)
    min_i = np.arange(len(gb_energies))[gb_energies == min_gb_energy][0]
    
    results = {}
    results['gb_energies'] = gb_energies
    results['min_gb_energy'] = min_gb_energy
    results['dumpfile_final'] = f'{min_i}.dump'
    results['symbols_final'] = system.symbols
    
    return results


def grain_boundary_relax(lammps_command: str,
                         system: am.System,
                         potential: lmp.Potential,
                         mpi_command: Optional[str] = None,
                         etol: float = 0.0,
                         ftol: float = 0.0,
                         maxiter: int = 10000,
                         maxeval: int = 100000,
                         dmax: float = uc.set_in_units(0.01, 'angstrom'),
                         lammps_date = None,
                         cutboxvector = 'c', 
                         gbindex: int = 0) -> dict:
    """
    Sets up and runs an energy/force minimization using LAMMPS for a single
    grain boundary configuration.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The grain boundary system to perform the relaxation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
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
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    if lammps_date is None:
        lammps_date = lmp.checkversion(lammps_command)['date']
        
    lammps_variables = {}
    
    system_info = system.dump('atom_data', f=f'gb-{gbindex}.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['dmax'] = dmax
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] =  maxeval
    
    # Set box relax direction based on cutboxvector orientation
    box2cart = {'a':'x', 'b':'y', 'c':'z'}
    lammps_variables['box_relax_direction'] = box2cart[cutboxvector]
    
    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
        
    # Write lammps input script
    lammps_script = 'gbmin.in'
        
    template = read_calc_file('iprPy.calculation.grain_boundary_static',
                              'gbmin.template')
    
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps to relax perfect.dat
    output = lmp.run(lammps_command, script_name=lammps_script, logfile=f'log-{gbindex}.lammps',
                     mpi_command=mpi_command)
    
    # Extract total final potential energy
    thermo = output.simulations[0].thermo
    total_pe = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    
    # Rename and clean up dump files
    finalstep = thermo.Step.values[-1]
    Path(f'atom.{finalstep}').rename(f'{gbindex}.dump')
    for atomfile in Path('.').glob('atom.*'):
        atomfile.unlink()
    
    results = {}
    results['gbindex'] = gbindex
    results['potentialenergy'] = total_pe
    
    return results

