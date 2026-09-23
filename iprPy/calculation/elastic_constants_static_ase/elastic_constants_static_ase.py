# Python script created by Lucas Hale

# Standard library imports
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat
from atomman.ase import optimizer

import ase
from ase.calculators.calculator import Calculator

def elastic_constants_static_ase(atoms: ase.Atoms,
                                 calculator: Calculator,
                                 strain: float = 1e-6,
                                 optimizer_style: str = 'LBFGSLineSearch',
                                 optimizer_kwargs: Optional[dict] = None,
                                 fmax: unitfloat = 1e-6) -> dict:
    """
    Computes the elastic constants of an atomic configuration using small
    strains.  This calculation is comparable to the LAMMPS ELASTIC example.
    
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
    strain : float, optional
        The small strain value to apply when calculating the elastic
        constants (default is 1e-6).
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
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'raw_Cij_negative'** (*numpy.ndarray*) - The values of Cij obtained
          from only the negative strains.
        - **'raw_Cij_positive'** (*numpy.ndarray*) - The values of Cij obtained
          from only the positive strains.
        - **'C'** (*atomman.ElasticConstants*) - The computed elastic constants
          obtained from averaging the negative and positive strain values.
    """
    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    # Convert values given with units if needed
    fmax = uc.set_in_units(fmax)

    atoms.calc = calculator

    # Get initial stresses
    stress0 = atoms.get_stress()

    # Loop over strain states
    allstress = np.empty([12, 6])
    strain_states = ['-x', '+x', '-y', '+y', '-z', '+z', 
                    '-yz', '+yz', '-xz', '+xz', '-xy', '+xy']
    for i, state in enumerate(strain_states):

        # Apply the strain, relax and compute stresses
        strained_atoms = add_strain(atoms, state, strain)
        strained_atoms.calc = calculator  
        opt = optimizer(optimizer_style, strained_atoms,
                        logfile=f'{state}.log', **optimizer_kwargs)
        opt.run(fmax=fmax)
        allstress[i] = strained_atoms.get_stress()


    # Negative strains
    cij_n = np.empty((6,6))
    for i in range(6):
        j = i * 2
        
        # Pull out strained state
        stress = allstress[j]
        
        # Calculate cij_n using stress changes
        cij_n[i] = (stress - stress0) / -strain
    
    # Positive strains
    cij_p = np.empty((6,6))
    for i in range(6):
        j = 1 + i * 2

        # Pull out strained state
        stress = allstress[j]
        
        # Calculate cij_p using stress changes
        cij_p[i] = (stress - stress0) / strain
    
    # Average symmetric values
    cij = (cij_n + cij_p) / 2
    for i in range(6):
        for j in range(i):
            cij[i,j] = cij[j,i] = (cij[i,j] + cij[j,i]) / 2
    
    # Define results_dict
    results_dict = {}
    results_dict['raw_Cij_negative'] = cij_n
    results_dict['raw_Cij_positive'] = cij_p
    results_dict['C'] = am.ElasticConstants(Cij=cij)
    
    return results_dict


def add_strain(atoms, state, strain):
    """
    atoms : ase.Atoms
        The unstrained configuration.
    state : str
        The sign for the shear (+ or -) followed by the direction
        (x, y, z, xz, yz, or xy) without spaces.
    strain : float
        The amount of strain to add.

    Returns
    -------
    strained_atoms: ase.Atoms
        A new atoms object with the applied strain state.
    """
    # Define default zero-strain state
    ϵ = {}
    ϵ['x'] = 1.0
    ϵ['y'] = 1.0
    ϵ['z'] = 1.0
    ϵ['xy'] = 0.0
    ϵ['xz'] = 0.0
    ϵ['yz'] = 0.0
    
    # Check strain state sign values and flip strain if negative
    sign = state[0]
    if sign not in ['+', '-']:
        raise ValueError('invalid strain state sign')
    elif sign == '-':
        strain = -strain

    # Check strain state direction
    direction = state[1:]
    if direction not in ϵ:
        raise ValueError('invalid strain state orientation')

    if len(direction) == 1:
        # Apply a normal strain 
        ϵ[direction] = 1.0 + strain
    else:
        # Apply a shear strain 
        ϵ[direction] = strain / 2

    # Define the deformation tensor
    deform = np.array([[ϵ['x'], ϵ['xy'], ϵ['xz']],
                       [ϵ['xy'], ϵ['y'], ϵ['yz']],
                       [ϵ['xz'], ϵ['yz'], ϵ['z']]])

    # Create a deformed cell
    new_cell = np.dot(atoms.get_cell(), deform.T)
    
    # Create a new atoms object and strain it
    strained_atoms = atoms.copy()
    strained_atoms.set_cell(new_cell, scale_atoms=True)

    return strained_atoms