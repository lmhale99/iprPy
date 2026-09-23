# Python script created by Lucas Hale

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat

import ase
from ase.calculators.calculator import Calculator


def diatom_scan_ase(calculator: Calculator,
                    symbols: list,
                    rmin: unitfloat = '0.02 angstrom',
                    rmax: unitfloat = '6.0 angstrom',
                    rsteps: int = 300) -> dict:
    """
    Performs a diatom energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    calculator : ase.calculators.calculator.Calculator
            The ase Calculator to use
    symbols : list
        The potential symbols associated with the two atoms in the diatom.
    rmin : float or str, optional
        The minimum r spacing to use (default value is 0.02 angstroms).
    rmax : float or str, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 300).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'energy_values'** (*numpy.array of float*) - The computed potential
          energies for each r value.
    """

    # Convert values given with units if needed
    rmin = uc.set_in_units(rmin)
    rmax = uc.set_in_units(rmax)

    # Check symbols values
    symbols = am.tools.aslist(symbols)
    if len(symbols) == 1:
        symbols = [symbols[0], symbols[0]]
    elif len(symbols) > 2:
        raise ValueError('symbols must have one or two values')
    
    # Initialize atoms object with two atoms
    a = rmax + 1
    pos = np.array([[0.1, 0.1, 0.1],
                    [0.1, 0.1, 0.1]])
    atoms = ase.Atoms(symbols=symbols,
                      positions=pos,
                      cell=[(a, 0, 0), (0, a, 0), (0, 0, a)],
                      pbc=False)

    # Assign the calculator
    atoms.calc = calculator

    # Initialize rijs and energies arrays
    rijs = np.linspace(rmin, rmax, rsteps)
    energies = np.empty_like(rijs)

    for i, rij in enumerate(rijs):

        # Update atom 2's x coordinate
        atoms.positions[1,0] = rij + 0.1
        
        # Get potential energy
        energies[i] = atoms.get_potential_energy()

    # Convert units on energies
    energies = uc.set_in_units(energies, 'eV')

    # Collect results
    results_dict = {}
    results_dict['r_values'] = rijs
    results_dict['energy_values'] = energies
    
    return results_dict
