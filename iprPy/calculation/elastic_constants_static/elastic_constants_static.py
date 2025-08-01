# coding: utf-8

# Python script created by Lucas Hale
# Built around LAMMPS script by Steve Plimpton

# Standard library imports
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def elastic_constants_static(lammps_command: str,
                             system: am.System,
                             potential: lmp.Potential,
                             mpi_command: Optional[str] = None,
                             strainrange: float = 1e-6,
                             etol: float = 0.0,
                             ftol: float = 0.0,
                             maxiter: int = 10000,
                             maxeval: int = 100000,
                             dmax: float = uc.set_in_units(0.01, 'angstrom')) -> dict:
    """
    Computes the elastic constants of an atomic configuration using small
    strains.  This calculation is comparable to the LAMMPS ELASTIC example.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    strainrange : float, optional
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

    # Convert hexagonal cells to orthorhombic to avoid LAMMPS tilt issues
    if am.tools.ishexagonal(system.box):
        system = system.rotate([[2,-1,-1,0], [0, 1, -1, 0], [0,0,0,1]])
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['restart_commands'] = restart_commands(potential, system.symbols)
    lammps_variables['strainrange'] = strainrange
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Fill in template files
    lammps_script = 'cij.in'
    template = read_calc_file('iprPy.calculation.elastic_constants_static',
                              'cij.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command)
    
    # Pull out initial state
    thermo = output.simulations[0]['thermo']
    pxx0 = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
    pyy0 = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
    pzz0 = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
    pyz0 = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
    pxz0 = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
    pxy0 = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
    
    # Negative strains
    cij_n = np.empty((6,6))
    for i in range(6):
        j = 1 + i * 2
        # Pull out strained state
        thermo = output.simulations[j]['thermo']
        pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
        pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
        pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
        pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
        pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
        pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
        
        # Calculate cij_n using stress changes
        cij_n[i] = np.array([pxx - pxx0, pyy - pyy0, pzz - pzz0,
                             pyz - pyz0, pxz - pxz0, pxy - pxy0]) / strainrange
    
    # Positive strains
    cij_p = np.empty((6,6))
    for i in range(6):
        j = 2 + i * 2
        # Pull out strained state
        thermo = output.simulations[j]['thermo']
        pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
        pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
        pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
        pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
        pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
        pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
        
        # Calculate cij_p using stress changes
        cij_p[i] = np.array([pxx - pxx0, pyy - pyy0, pzz - pzz0,
                              pyz - pyz0, pxz - pxz0, pxy - pxy0]) / -strainrange
    
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

def restart_commands(potential: lmp.Potential,
                     symbols: list) -> str:
    """
    Command lines to restart calculation from the initial relaxation

    Parameters
    ----------
    potential : lmp.Potential
        The interatomic potential.
    symbols : list
        The list of symbol models associated with the interatomic potential.
    """

    if potential.pair_style == 'kim':
        pair_info = potential.pair_info(symbols)
        commands = '\n'.join([
            pair_info.split('\n')[0],
            'read_restart initial.restart',
        ])
        commands += '\n' + '\n'.join(pair_info.split('\n')[1:])

    else:
        commands = '\n'.join([
            'read_restart initial.restart',
            potential.pair_info(symbols),
        ])

    commands += '\n'.join([
        '',
        '# Setup minimization style',
        'min_modify dmax ${dmax}',
        '',
        '# Setup output',
        'thermo_style custom step lx ly lz yz xz xy pxx pyy pzz pyz pxz pxy v_peatom pe',
        'thermo_modify format float %.13e'])
    
    return commands