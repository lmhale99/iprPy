# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from copy import deepcopy
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import unitfloat
from atomman.ase import optimizer

import ase
from ase.calculators.calculator import Calculator

def point_defect_static_ase(atoms: ase.Atoms,
                            calculator: Calculator,
                            point_kwargs: Union[list, dict],
                            cutoff: unitfloat,
                            optimizer_style: str = 'LBFGSLineSearch',
                            optimizer_kwargs: Optional[dict] = None,
                            fmax: unitfloat = 1e-8,
                            tol: unitfloat = '1e-5 angstrom') -> dict:
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy. Evaluates a relaxed system containing a point defect
    to determine if the defect structure has transformed to a different
    configuration.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float or str
        Cutoff distance to use in identifying neighbor atoms.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simulation in.  If not
        given, will use the current working directory.
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
    tol : float or str, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_pot'** (*float*) - The per-atom potential energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
          relaxed defect system.
        - **'pij_tensor'** (*numpy.ndarray of float*) - The elastic dipole
          tensor associated with the defect.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed defect system.
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
          has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.ndarray of float*) - The centrosummation
          parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.ndarray of float*) - The position_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.ndarray of float*) - The db_vect_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for dumbbell-style defects.
    """
    
    # Run ptd_energy to refine values
    results_dict = point_defect_relax(atoms,
                                      calculator,
                                      point_kwargs,
                                      optimizer_style=optimizer_style,
                                      optimizer_kwargs=optimizer_kwargs,
                                      fmax = fmax)
    
    # Run check_ptd_config
    results_dict2 = check_ptd_config(results_dict['system_ptd'],
                                     point_kwargs,
                                     cutoff, tol)
    results_dict.update(results_dict2)

    return results_dict

def point_defect_relax(atoms: ase.Atoms,
                       calculator: Calculator,
                       point_kwargs: Union[list, dict],
                       optimizer_style: str = 'LBFGSLineSearch',
                       optimizer_kwargs: Optional[dict] = None,
                       fmax: unitfloat = 1e-6) -> dict:
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simulation in.  If not
        given, will use the current working directory.
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
        
        - **'E_pot'** (*float*) - The per-atom potential energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
          relaxed defect system.
        - **'pij_tensor'** (*numpy.ndarray of float*) - The elastic dipole
          tensor associated with the defect.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed defect system.
    """
    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    # Convert values given with units if needed
    fmax = uc.set_in_units(fmax)

    
    # Relax base system with an energy/force minimization
    atoms.calc = calculator
    opt = optimizer(optimizer_style, atoms, logfile='base.log',
                    **optimizer_kwargs)
    opt.run(fmax=fmax)

    # Extract energy and pressures of base
    Epot_base = atoms.get_potential_energy()
    Epot_base_atom = Epot_base / len(atoms)
    pressure_base = -atoms.get_stress(voigt = False)
    
    # Convert atoms to an atomman system to add ptd(s)
    system_base = am.load('ase_Atoms', atoms)
    system_ptd = deepcopy(system_base)
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        system_ptd = am.defect.point(system_ptd, **pkwargs)
    atoms_ptd = system_ptd.dump('ase_Atoms')

    # Relax defect system with an energy/force minimization
    atoms_ptd.calc = calculator
    opt = optimizer(optimizer_style, atoms_ptd, logfile='ptd.log',
                    **optimizer_kwargs)
    opt.run(fmax=fmax)

    # Extract energy and pressures of ptd
    Epot_ptd = atoms_ptd.get_potential_energy()
    pressure_ptd = -atoms_ptd.get_stress(voigt = False)
    system_ptd = am.load('ase_Atoms', atoms_ptd)
    
    # Compute defect formation energy
    E_ptd_f = Epot_ptd - Epot_base_atom * len(atoms_ptd)
    
    # Compute strain tensor
    pij = -(pressure_base - pressure_ptd) * atoms.cell.volume
    
    # Cleanup files
    for fname in Path.cwd().glob('atom.*'):
        fname.unlink()
    for dumpjsonfile in Path.cwd().glob('*.dump.json'):
        dumpjsonfile.unlink()
    
    # Return results
    results_dict = {}
    results_dict['E_pot'] = Epot_base_atom
    results_dict['E_ptd_f'] = E_ptd_f
    results_dict['E_total_base'] = Epot_base
    results_dict['E_total_ptd'] = Epot_ptd
    results_dict['pij_tensor'] = pij
    results_dict['system_base'] = system_base
    results_dict['system_ptd'] = system_ptd
    results_dict['dumpfile_base'] = 'perfect.dump'
    results_dict['dumpfile_ptd'] = 'defect.dump'
    
    return results_dict

def check_ptd_config(system: am.System,
                     point_kwargs: Union[list, dict],
                     cutoff: unitfloat,
                     tol: unitfloat = '1e-5 angstrom') -> dict:
    """
    Evaluates a relaxed system containing a point defect to determine if the
    defect structure has transformed to a different configuration.
    
    Parameters
    ----------
    system : atomman.System
        The relaxed defect system.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float
        Cutoff distance to use in identifying neighbor atoms.
    tol : float, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
          has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.ndarray of float*) - The centrosummation
          parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.ndarray of float*) - The position_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.ndarray of float*) - The db_vect_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for dumbbell-style defects.
    """
    # Convert values given with units if needed
    cutoff = uc.set_in_units(cutoff)
    tol = uc.set_in_units(tol)

    # Check if point_kwargs is a list
    if not isinstance(point_kwargs, (list, tuple)):
        pos = point_kwargs['pos']
    
    # If it is a list of 1, use that set
    elif len(point_kwargs) == 1:
        point_kwargs = point_kwargs[0]
        pos = point_kwargs['pos']
        
    # If it is a list of two (divacancy), use the first and average position
    elif len(point_kwargs) == 2:
        pos = (np.array(point_kwargs[0]['pos'])
               + np.array(point_kwargs[1]['pos'])) / 2
        point_kwargs = point_kwargs[0]
    
    # More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')

    # Initially set has_reconfigured to False
    has_reconfigured = False
    
    # Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.pos, pos) 
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    
    # Calculate centrosummation by summing up the positions of the close atoms
    centrosummation = np.sum(pos_vects[pos_mags < cutoff], axis=0)
    
    if not np.allclose(centrosummation, np.zeros(3), atol=tol):
        has_reconfigured = True
        
    # Calculate shift of defect atom's position if interstitial or substitutional
    if point_kwargs['ptd_type'] == 'i' or point_kwargs['ptd_type'] == 's':
        position_shift = system.dvect(system.natoms-1, pos)
       
        if not np.allclose(position_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation,
                'position_shift': position_shift}
        
    # Investigate if dumbbell vector has shifted direction 
    elif point_kwargs['ptd_type'] == 'db':
        db_vect = point_kwargs['db_vect'] / np.linalg.norm(point_kwargs['db_vect'])
        new_db_vect = system.dvect(-2, -1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation,
                'db_vect_shift': db_vect_shift}
    
    else:
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation}