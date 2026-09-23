# Python script created by Lucas Hale

# Standard Python libraries
from copy import deepcopy
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat

import ase
from ase.calculators.calculator import Calculator

def e_vs_r_scan_ase(atoms: ase.Atoms,
                    calculator: Calculator,
                    ucell: Optional[ase.Atoms] = None, 
                    rmin: unitfloat = '2.0 angstrom', 
                    rmax: unitfloat = '6.0 angstrom',
                    rsteps: int = 200) -> dict:
    """
    Performs a cohesive energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    atoms : ase.Atoms
        The atomic configuration to evaluate.
    calculator : ase.calculators.calculator.Calculator
        The ase Calculator to use.
    ucell : ase.Atoms, optional
        The fundamental unit cell corresponding to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as atoms.
    rmin : float or str, optional
        The minimum r spacing to use (default value is 2.0 angstroms).
    rmax : float or str, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 200).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'a_values'** (*numpy.array of float*) - All unit cell a lattice
          constants corresponding to the values explored.
        - **'Ecoh_values'** (*numpy.array of float*) - The computed cohesive
          energies for each r value.
        - **'min_cell'** (*list of ase.Atoms*) - Systems corresponding to
          the minima identified in the Ecoh_values.
    """

    # Convert values given with units if needed
    rmin = uc.set_in_units(rmin)
    rmax = uc.set_in_units(rmax)

    # Make atoms a deepcopy of itself (protect original from changes)
    atoms = deepcopy(atoms)
    atoms.calc = calculator
    
    # Set ucell = atoms if ucell not given
    if ucell is None:
        ucell = atoms
    
    # Calculate the r/a ratio for the unit cell
    r_a = am.ase.r0(ucell) / ucell.cell.lengths()[0]
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a, ly_a, lz_a = atoms.cell.lengths() / ucell.cell.lengths()[0]
    alpha, beta, gamma = atoms.cell.angles()
    b_a = ucell.cell.lengths()[1] / ucell.cell.lengths()[0]
    c_a = ucell.cell.lengths()[2] / ucell.cell.lengths()[0]
 
    # Build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    a_values = r_values / r_a
    Ecoh_values = np.empty(rsteps)
    natoms = len(atoms)

    # Loop over values
    for i in range(rsteps):
        
        # Rescale atom's cell
        a = a_values[i]
        atoms.set_cell([a * lx_a, a * ly_a, a * lz_a, alpha, beta, gamma], scale_atoms=True)
        
        # Evaluate energy using a run0 calculation
        try:
            Ecoh_values[i] = atoms.get_potential_energy() / natoms
        except:
            Ecoh_values[i] = np.inf

    # Throw error if all runs failed.
    if len(Ecoh_values[np.isfinite(Ecoh_values)]) == 0:
        raise ValueError('All evaluations failed. Potential likely invalid or incompatible.')
    
    # Find unit cell systems at the energy minimums
    min_cells = []
    for i in range(1, rsteps - 1):
        if (Ecoh_values[i] < Ecoh_values[i-1]
            and Ecoh_values[i] < Ecoh_values[i+1]):
            a = a_values[i]
            cell = deepcopy(ucell)
            cell.set_cell([a, a * b_a, a * c_a, alpha, beta, gamma], scale_atoms=True)
            min_cells.append(cell)
    
    # Collect results
    results_dict = {}
    results_dict['r_values'] = r_values
    results_dict['a_values'] = a_values
    results_dict['Ecoh_values'] = Ecoh_values
    results_dict['min_cell'] = min_cells
    
    return results_dict
