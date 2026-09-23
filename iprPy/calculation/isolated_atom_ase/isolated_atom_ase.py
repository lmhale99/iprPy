# Python script created by Lucas Hale

# Standard Python libraries
from typing import Optional, Union

import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am

import ase
from ase.calculators.calculator import Calculator

def isolated_atom_ase(calculator: Calculator,
                      symbols: Union[str, list, None] = None) -> dict:
    """
    Evaluates the isolated atom energy for each elemental model of a potential.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'energy'** (*dict*) - The computed potential energies for each
          symbol.
    """
    if symbols is None:
        symbols = calculator.elements
    else:
        symbols = am.tools.aslist(symbols)

    # Loop over symbols
    energydict = {}
    for i, symbol in enumerate(symbols):

        # Define atoms and add calculator
        atoms = ase.Atoms(symbols=[symbol], positions=[[0.5, 0.5, 0.5]],
                          cell=[1, 1, 1], pbc=False)
        atoms.calc = calculator
        energydict[symbol] = atoms.get_potential_energy()
        
    
    # Collect results
    results_dict = {}
    results_dict['energy'] = energydict
    
    return results_dict