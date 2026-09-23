# Python script created by Lucas Hale

# Standard library imports
from typing import Optional
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat
from atomman.ase import optimizer

import ase
from ase.filters import FrechetCellFilter
from ase.calculators.calculator import Calculator

def relax_static_ase(atoms: ase.Atoms,
                     calculator: Calculator,
                     optimizer_style: str = 'LBFGSLineSearch',
                     optimizer_kwargs: Optional[dict] = None,
                     fmax: unitfloat = 1e-5,
                     maxcycles: int = 100,
                     ctol: float = 1e-10,
                     raise_at_maxcycles: bool = False) -> dict:
    """
    Repeatedly run a static relaxation with box dimension relaxation
    until box dimensions no longer change.
    
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
    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    fmax = uc.set_in_units(fmax)

    atoms = atoms.copy()
    atoms.calc = calculator

    # Initialize parameters
    old_vects = deepcopy(atoms.cell.array)
    converged = False
    
    # Run minimizations up to maxcycles times
    for cycle in range(maxcycles):

        # Relax structure
        opt = optimizer(optimizer_style, FrechetCellFilter(atoms),
                        logfile=f'{cycle}.log')
        opt.run(fmax=fmax)
        new_vects = deepcopy(atoms.cell.array)

        # Test if box dimensions have converged
        if np.allclose(old_vects, new_vects, rtol=ctol, atol=0):
            converged = True
            break
        else:
            old_vects = deepcopy(new_vects)
    
    # Check for convergence
    if converged is False and raise_at_maxcycles is True:
        raise RuntimeError('Failed to converge after ' + str(maxcycles) + ' cycles')
    
    # Build results_dict
    results_dict = {}
    results_dict['atoms'] = atoms
    results_dict['E_pot'] = atoms.get_potential_energy() / len(atoms)

    box = am.Box(vects=atoms.cell.array)
    results_dict['lx'] = box.lx
    results_dict['ly'] = box.ly
    results_dict['lz'] = box.lz
    results_dict['xy'] = box.xy
    results_dict['xz'] = box.xz
    results_dict['yz'] = box.yz

    stress = atoms.get_stress()
    results_dict['measured_pxx'] = - stress[0]
    results_dict['measured_pyy'] = - stress[1]
    results_dict['measured_pzz'] = - stress[2]
    results_dict['measured_pxy'] = - stress[5]
    results_dict['measured_pxz'] = - stress[4]
    results_dict['measured_pyz'] = - stress[3]
    
    return results_dict

