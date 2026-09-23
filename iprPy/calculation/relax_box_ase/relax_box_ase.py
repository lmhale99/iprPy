# Python script created by Lucas Hale

# Standard Python libraries
from copy import deepcopy
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

import ase
from ase.calculators.calculator import Calculator

def relax_box_ase(atoms: ase.Atoms,
                  calculator: Calculator,
                  fmax: float = 1e-5)  -> dict:
    """
    Quickly relaxes an atomic configuration's box without updating the
    atomic coordinates.  
    
    Parameters
    ----------
    atoms : ase.Atoms
        The atomic configuration to evaluate.
    calculator : ase.calculators.calculator.Calculator
        The ase Calculator to use.
    fmax : float, optional
        The convergence criterion for the atomic forces.  Default value is
        1e-5.
    
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
        - **'measured_pxx'** (*float*) - The measured x tensile pressure of the
          relaxed system.
        - **'measured_pyy'** (*float*) - The measured y tensile pressure of the
          relaxed system.
        - **'measured_pzz'** (*float*) - The measured z tensile pressure of the
          relaxed system.
        - **'measured_pxy'** (*float*) - The measured xy shear pressure of the
          relaxed system.
        - **'measured_pxz'** (*float*) - The measured xz shear pressure of the
          relaxed system.
        - **'measured_pyz'** (*float*) - The measured yz shear pressure of the
          relaxed system.
    
    Raises
    ------
    RuntimeError
        If system diverges or no convergence reached after 100 cycles.
    """
    # Make atoms a deepcopy of itself (protect original from changes)
    atoms = deepcopy(atoms)
    atoms.calc = calculator

    atomsfilter = ase.filters.StrainFilter(atoms, mask=[True, True, True, False, False, False])
    dyn = ase.optimize.BFGS(atomsfilter)

    # Run until forces and stresses are small
    dyn.run(fmax=1e-5)

    # Initialize results dict and extract values
    results_dict = {}
    results_dict['atoms'] = atoms
    results_dict['E_pot'] = uc.set_in_units(atoms.get_potential_energy(), 'eV') / len(atoms)
    stress = uc.set_in_units(atoms.get_stress(), 'eV/angstrom^3')
    results_dict['measured_pxx'] = - stress[0]
    results_dict['measured_pyy'] = - stress[1]
    results_dict['measured_pzz'] = - stress[2]
    results_dict['measured_pxy'] = - stress[5]
    results_dict['measured_pxz'] = - stress[4]
    results_dict['measured_pyz'] = - stress[3]

    box = am.Box(vects=atoms.cell.array)
    results_dict['lx'] = box.lx
    results_dict['ly'] = box.ly
    results_dict['lz'] = box.lz
    results_dict['xy'] = box.xy
    results_dict['xz'] = box.xz
    results_dict['yz'] = box.yz