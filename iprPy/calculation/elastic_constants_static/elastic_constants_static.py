# Python script created by Lucas Hale
# Originally based on the LAMMPS example script by Steve Plimpton

# Standard library imports
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

def elastic_constants_static(lammps_command: Union[str, LAMMPSobj],
                             system: am.System,
                             potential: lammpspotential,
                             mpi_command: Optional[str] = None,
                             strainrange: float = 1e-6,
                             etol: float = 0.0,
                             ftol: unitfloat = 0.0,
                             maxiter: int = 10000,
                             maxeval: int = 100000,
                             dmax: unitfloat = '0.01 angstrom',
                             usefiles: bool = True) -> dict:
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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    ftol = uc.set_in_units(ftol)
    dmax = uc.set_in_units(dmax)

    # Convert hexagonal cells to orthorhombic to avoid LAMMPS tilt issues
    if am.tools.ishexagonal(system.box):
        system = system.rotate([[2,-1,-1,0], [0, 1, -1, 0], [0,0,0,1]])

    # Call exe or lib function version for LAMMPS calculation
    all_thermo = cij_static(lmp, system, potential,
                            strainrange=strainrange,
                            etol=etol, ftol=ftol, maxiter=maxiter,
                            maxeval=maxeval, dmax=dmax)
    

    # Pull out initial state
    pxx0 = all_thermo.Pxx.values[0]
    pyy0 = all_thermo.Pyy.values[0]
    pzz0 = all_thermo.Pzz.values[0]
    pyz0 = all_thermo.Pyz.values[0]
    pxz0 = all_thermo.Pxz.values[0]
    pxy0 = all_thermo.Pxy.values[0]
    
    # Negative strains
    cij_n = np.empty((6,6))
    for i in range(6):
        j = 1 + i * 2
        
        # Pull out strained state
        pxx = all_thermo.Pxx.values[j]
        pyy = all_thermo.Pyy.values[j]
        pzz = all_thermo.Pzz.values[j]
        pyz = all_thermo.Pyz.values[j]
        pxz = all_thermo.Pxz.values[j]
        pxy = all_thermo.Pxy.values[j]
        
        # Calculate cij_n using stress changes
        cij_n[i] = np.array([pxx - pxx0, pyy - pyy0, pzz - pzz0,
                             pyz - pyz0, pxz - pxz0, pxy - pxy0]) / strainrange
    
    # Positive strains
    cij_p = np.empty((6,6))
    for i in range(6):
        j = 2 + i * 2

        # Pull out strained state
        pxx = all_thermo.Pxx.values[j]
        pyy = all_thermo.Pyy.values[j]
        pzz = all_thermo.Pzz.values[j]
        pyz = all_thermo.Pyz.values[j]
        pxz = all_thermo.Pxz.values[j]
        pxy = all_thermo.Pxy.values[j]
        
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

def cij_static(lmp: LAMMPSobj,
               system: am.System,
               potential: lammpspotential,
               strainrange: float = 1e-6,
               etol: float = 0.0,
               ftol: float = 0.0,
               maxiter: int = 10000,
               maxeval: int = 100000,
               dmax: float = 0.01,
               usefiles: bool = False) -> pd.DataFrame:
    
    if usefiles:
        logfile = 'log.lammps'
        script = 'cij.in'
    else:
        logfile = 'none'
        script = None

    thermo = []

    # Specify common variables (retained after resets)
    lmp.cmd.variable('strain', 'equal', strainrange)
    lmp.cmd.variable('etol', 'equal', etol)
    lmp.cmd.variable('ftol', 'equal', uc.get_in_units(ftol, lmp.unitsdict['force']))
    lmp.cmd.variable('maxiter', 'equal', maxiter)
    lmp.cmd.variable('maxeval', 'equal', maxeval)
    lmp.cmd.variable('dmax', 'equal', uc.get_in_units(dmax, lmp.unitsdict['length']))

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', potential=potential,
                                  tilt_large=True, usefiles=usefiles, logfile=logfile)
    
    # Set initial configuration's dimensions as variables (retained after resets)
    lmp.cmd.variable('lx0', 'equal', '$(lx)')
    lmp.cmd.variable('ly0', 'equal', '$(ly)')
    lmp.cmd.variable('lz0', 'equal', '$(lz)')

    # Specify the thermo properties to calculate
    lmp.cmd.variable('peatom', 'equal', 'pe/atoms')

    # Set up minimization style and thermo info
    lmp.cmd.min_modify('dmax', '${dmax}') 
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'yz', 'xz', 'xy', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'v_peatom', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Run initial minimization
    lmp.cmd.minimize('${etol}', '${ftol}', '${maxiter}', '${maxeval}')
    
    if lmp.islib:
        # Get thermo data and relaxed system0
        thermo.append(lmp.last_thermo())
        system0 = am.load('lammps_lib', lmp, symbols=system.symbols)
    else:
        # Define restart
        lmp.cmd.write_restart('initial.restart')
        system0 = system

    shear_states = ['-x', '+x', '-y', '+y', '-z', '+z', 
                    '-yz', '+yz', '-xz', '+xz', '-xy', '+xy']
    for state in shear_states:

        # Reset system to the restart/original system
        lmp.new_system_from_restart(filename='initial.restart', system=system0,
                                    potential=potential, tilt_large=True,
                                    usefiles=usefiles)

        # Redo setup minimization style and thermo info
        lmp.cmd.min_modify('dmax', '${dmax}') 
        lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'yz', 'xz', 'xy', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'v_peatom', 'pe')
        lmp.cmd.thermo_modify('format', 'float', '%.17e')

        # Apply the strain state
        add_strain(lmp, state)

        # Run minimization
        lmp.cmd.minimize('${etol}', '${ftol}', '${maxiter}', '${maxeval}')
        if lmp.islib and not usefiles:
            # Get thermo data
            thermo.append(lmp.last_thermo())

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    if log is None:
        # Compile thermo into a pandas DataFrame
        thermo = pd.DataFrame(thermo)
    else:
        # Get thermo from log output
        thermo = log.flatten('all').thermo
        thermo = thermo[thermo.index % 2 == 1].reset_index(drop=True)

    # Convert units on thermo terms
    lmp.set_thermo_units(thermo)
    
    return thermo

def add_strain(lmp, state: str):
    """
    Applies a strain state
    
    Parameters
    ----------
    state : str
        The sign for the shear (+ or -) followed by the direction
        (x, y, z, xz, yz, or xy) without spaces.
    """
    # Build inputs based on state value
    sign = state[0]
    if sign == '+':
        sign = ''
    ref = state[-1]   # length reference is normal direction or last direction in shear
    delta = f'{sign}${{strain}}*${{l{ref}0}}'
    direction = state[1:]

    # Call LAMMPS commands
    lmp.cmd.variable('delta', 'equal', delta)
    if len(direction) == 1:
        lmp.cmd.change_box('all', direction, 'delta', 0, '${delta}', 'remap', 'units', 'box')
    else:
        lmp.cmd.change_box('all', direction, 'delta', '${delta}', 'remap', 'units', 'box')