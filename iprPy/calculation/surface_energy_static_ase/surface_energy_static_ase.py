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
from atomman.typing import unitfloat, lammps, millerindices
from atomman.ase import optimizer

import ase
from ase.calculators.calculator import Calculator

def surface_energy_static_ase(atoms: ase.Atoms,
                              calculator: Calculator,
                              hkl: millerindices,
                              sizemults: Union[list, tuple, None] = None,
                              minwidth: Optional[unitfloat] = None,
                              even: bool = False,
                              conventional_setting: str = 'p',
                              cutboxvector: str = 'c',
                              atomshift: Union[list, np.ndarray, None] = None,
                              shiftindex: Optional[int] = None,
                              optimizer_style: str = 'LBFGSLineSearch',
                              optimizer_kwargs: Optional[dict] = None,
                              fmax: unitfloat = 1e-6) -> dict:
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
    if optimizer_kwargs is None:
            optimizer_kwargs = {}

    # Convert values given with units if needed
    if minwidth is not None:
        minwidth = uc.set_in_units(minwidth)
    fmax = uc.set_in_units(fmax)

    # Construct free surface configuration generator
    ucell = am.load('ase_Atoms', atoms)
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

    # Convert bulk and defect system to ase.Atoms
    atoms_surf = system.dump('ase_Atoms')
    system.pbc = [True, True, True]
    atoms_base = system.dump('ase_Atoms')

    # Evaluate system with free surface
    atoms_surf.calc = calculator
    opt = optimizer(optimizer_style, atoms_surf, logfile='surf.log',
                    **optimizer_kwargs)
    opt.run(fmax=fmax)
    Epot_surf = atoms_surf.get_potential_energy()

    # Evaluate perfect system (all pbc removes cut)
    atoms_base.calc = calculator
    opt = optimizer(optimizer_style, atoms_base, logfile='base.log',
                    **optimizer_kwargs)
    opt.run(fmax=fmax)
    Epot_base = atoms_base.get_potential_energy()
    
    # Compute the free surface formation energy
    E_surf_f = (Epot_surf - Epot_base) / (2 * A_surf)
    
    # Save values to results dictionary
    results_dict = {}
    
    results_dict['atoms_base'] = atoms_base
    results_dict['atoms_surf'] = atoms_surf
    results_dict['E_total_base'] = Epot_base
    results_dict['E_total_surf'] = Epot_surf
    results_dict['A_surf'] = A_surf
    results_dict['E_pot'] = Epot_base / len(atoms_base)
    results_dict['E_surf_f'] = E_surf_f
    
    return results_dict
