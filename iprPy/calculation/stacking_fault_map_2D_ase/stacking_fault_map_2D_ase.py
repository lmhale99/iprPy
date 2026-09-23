# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from pathlib import Path
from typing import Optional, Union
import shutil

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat, lammps, millerindices
from atomman.lammps import LAMMPS, LAMMPSobj
from atomman.ase import optimizer

import ase
from ase.constraints import FixedLine
from ase.calculators.calculator import Calculator

def stackingfaultmap(atoms: ase.Atoms,
                     calculator: Calculator,
                     hkl: millerindices,
                     sizemults: Union[list, tuple, None] = None,
                     minwidth: Optional[unitfloat] = None,
                     even: bool = False,
                     a1vect_uvw: Union[millerindices] = None,
                     a2vect_uvw: Union[millerindices] = None,
                     conventional_setting: str = 'p',
                     cutboxvector: str = 'c',
                     faultpos_rel: Optional[float] = None,
                     faultpos_cart: Optional[float] = None,
                     num_a1: int = 10,
                     num_a2: int = 10,
                     atomshift: Union[list, np.ndarray, None] = None,
                     shiftindex: Optional[int] = None,
                     optimizer_style: str = 'LBFGSLineSearch',
                     optimizer_kwargs: Optional[dict] = None,
                     fmax: unitfloat = 1e-6) -> dict:
    """
    Computes a generalized stacking fault map for shifts along a regular 2D
    grid.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    ucell : atomman.System
        The crystal unit cell to use as the basis of the stacking fault
        configurations.
    potential : aPotentialLAMMPS or PotentialLAMMPSKIM
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
    a1vect_uvw : array-like object or str, optional
        The crystal vector to use for one of the two shifting vectors.  If
        not given, will be set to the shortest in-plane lattice vector.
    a2vect_uvw : array-like object or str, optional
        The crystal vector to use for one of the two shifting vectors.  If
        not given, will be set to the shortest in-plane lattice vector not
        parallel to a1vect_uvw.
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
    faultpos_rel : float, optional
        The position to place the slip plane within the system given as a
        relative coordinate along the out-of-plane direction.  faultpos_rel
        and faultpos_cart cannot both be given.  Default value is 0.5 if 
        faultpos_cart is also not given.
    faultpos_cart : float, optional
        The position to place the slip plane within the system given as a
        Cartesian coordinate along the out-of-plane direction.  faultpos_rel
        and faultpos_cart cannot both be given.
    num_a1 : int, optional
        The number of fractional coordinates to evaluate along a1vect_uvw.
        Default value is 10.
    num_a2 : int, optional
        The number of fractional coordinates to evaluate along a2vect_uvw.
        Default value is 10.
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
        
        - **'A_fault'** (*float*) - The area of the fault surface.
        - **'gamma'** (*atomman.defect.GammaSurface*) - A gamma surface
          plotting object.
    """
    # Convert values given with units if needed
    if minwidth is not None:
        minwidth = uc.set_in_units(minwidth)
    fmax = uc.set_in_units(fmax)

    # Construct stacking fault configuration generator
    ucell = am.load('ase_Atoms', atoms)
    gsf_gen = am.defect.StackingFault(hkl, ucell, cutboxvector=cutboxvector,
                                      a1vect_uvw=a1vect_uvw, a2vect_uvw=a2vect_uvw,
                                      conventional_setting=conventional_setting)
    
    # Check shift parameters
    if shiftindex is not None:
        assert atomshift is None, 'shiftindex and atomshift cannot both be given'
        atomshift = gsf_gen.shifts[shiftindex]
    elif atomshift is None:
        atomshift = gsf_gen.shifts[0]
    
    # Generate the free surface (zero-shift) configuration
    gsf_gen.surface(shift=atomshift, minwidth=minwidth, sizemults=sizemults,
                    even=even, faultpos_rel=faultpos_rel,
                    faultpos_cart=faultpos_cart)
    
    abovefault = gsf_gen.abovefault
    cutindex = gsf_gen.cutindex
    A_fault = gsf_gen.surfacearea

    # Define lists
    a1vals = []
    a2vals = []
    E_totals = []
    disps = []

    # Loop over all shift combinations
    for a1, a2, sfsystem in gsf_gen.iterfaultmap(num_a1=num_a1, num_a2=num_a2):
        a1vals.append(a1)
        a2vals.append(a2)

        # Evaluate the system at the shift
        tag = f'a{a1:.10f}-b{a2:.10f}'
        sfatoms = sfsystem.dump('ase_Atoms')
        stackingfaultrelax(sfatoms, calculator, cutboxvector=cutboxvector,
                           fmax=fmax, optimizer_style=optimizer_style,
                           optimizer_kwargs=optimizer_kwargs,
                           logfile=f'{tag}.log')
        
        # Extract terms
        E_totals.append(sfatoms.get_potential_energy())
        pos = sfatoms.get_positions()
        disps.append(pos[abovefault, cutindex].mean()
                   - pos[~abovefault, cutindex].mean())
        

    E_totals = np.array(E_totals)
    disps = np.array(disps)
    
    # Get zeroshift values
    E_total_0 = E_totals[0]
    disp_0 = disps[0]
    
    # Compute the stacking fault energies
    E_gsfs = (E_totals - E_total_0) / A_fault
    
    # Compute the change in displacement normal to fault plane
    delta_disps = disps - disp_0
    
    results_dict = {}
    results_dict['A_fault'] = A_fault
    results_dict['gamma'] = am.defect.GammaSurface(a1vect = gsf_gen.a1vect_uvw,
                                                   a2vect = gsf_gen.a2vect_uvw,
                                                   box = gsf_gen.ucell.box,
                                                   a1 = a1vals,
                                                   a2 = a2vals,
                                                   E_gsf = E_gsfs,
                                                   delta = delta_disps)

    return results_dict

def stackingfaultrelax(atoms,
                       calculator,
                       cutboxvector: str = 'c',
                       optimizer_style: str = 'LBFGSLineSearch',
                       optimizer_kwargs: Optional[dict] = None,
                       fmax: float = 0.0,
                       logfile: str = 'sf.log'):
    """
    Perform a stacking fault relaxation simulation for a single fault shift
    in which atoms can only relax normal to the fault plane.
    
    Parameters
    ----------
    
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', has
        the non-periodic boundary (default is 'c').  Fault plane normal is
        defined by the cross of the other two box vectors.
        
    """
    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    if cutboxvector == 'a':
        relaxdirection = [1, 0, 0]
    elif cutboxvector == 'b':
        relaxdirection = [0, 1, 0]
    elif cutboxvector == 'c':
        relaxdirection = [0, 0, 1]
    else: 
        raise ValueError('Invalid cutboxvector')

    # Set calculator and constraint
    atoms.calc = calculator
    c = FixedLine(
        indices=[atom.index for atom in atoms],
        direction=relaxdirection,
    )
    atoms.set_constraint(c)

    # Relax
    opt = optimizer(optimizer_style, atoms, logfile=logfile,
                    **optimizer_kwargs)
    opt.run(fmax=fmax)