# Python script created by Lucas Hale

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

import ase
from ase.calculators.calculator import Calculator

def energy_check_ase(atoms: ase.Atoms,
                     calculator: Calculator,
                     dumpforces: bool = False) -> dict:
    """
    Performs a quick run 0 calculation to evaluate the potential energy of a
    configuration.
    
    Parameters
    ----------
    atoms : ase.Atoms
        The atomic configuration to evaluate.
    calculator : ase.calculators.calculator.Calculator
        The ase Calculator to use.
    forces : bool, optional
        If True, the atomic forces will also be calculated and returned.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'PotEng'** (*float*) - The total potential energy of the system.
        - **'PotEngAtom'** (*float*) - The per-atom potential energy of the system.
        - **'Pxx'** (*float*) - The measured xx component of the pressure on the system.
        - **'Pyy'** (*float*) - The measured yy component of the pressure on the system.
        - **'Pzz'** (*float*) - The measured zz component of the pressure on the system.
        - **'Pxy'** (*float*) - The measured xy component of the pressure on the system.
        - **'Pxz'** (*float*) - The measured xz component of the pressure on the system.
        - **'Pyz'** (*float*) - The measured yz component of the pressure on the system.
        - **'F'** (*numpy.ndarray*) - The atomic forces, returned if forces is True.
    """
    # Set the calculator to the atoms configuration
    atoms.calc = calculator

    # Initialize results dict and extract values
    results_dict = {}
    results_dict['PotEng'] = uc.set_in_units(atoms.get_potential_energy(), 'eV')
    results_dict['PotEngAtom'] = results_dict['PotEng'] / len(atoms)
    stress = uc.set_in_units(atoms.get_stress(), 'eV/angstrom^3')
    results_dict['measured_pxx'] = - stress[0]
    results_dict['measured_pyy'] = - stress[1]
    results_dict['measured_pzz'] = - stress[2]
    results_dict['measured_pxy'] = - stress[5]
    results_dict['measured_pxz'] = - stress[4]
    results_dict['measured_pyz'] = - stress[3]
    if dumpforces:
        results_dict['F'] = uc.set_in_units(atoms.get_forces(), 'eV/angstrom')

    return results_dict