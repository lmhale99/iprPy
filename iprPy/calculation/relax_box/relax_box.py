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

def relax_box(lammps_command: Union[str, LAMMPSobj],
              system: am.System,
              potential: lammpspotential,
              mpi_command: Optional[str] = None,
              strainrange: float = 1e-6,
              pxx: unitfloat = 0.0,
              pyy: unitfloat = 0.0,
              pzz: unitfloat = 0.0,
              pxy: unitfloat = 0.0,
              pxz: unitfloat = 0.0,
              pyz: unitfloat = 0.0,
              tol: float = 1e-10,
              diverge_scale: float = 3.0,
              usefiles: bool = False)  -> dict:
    """
    Quickly refines static orthorhombic system by evaluating the elastic
    constants and the virial pressure.
    
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
    pxx : float, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    pyy : float, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    pzz : float, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    pxy : float, optional
        The value to relax the xy shear pressure component to (default is
        0.0).
    pxz : float, optional
        The value to relax the xz shear pressure component to (default is
        0.0).
    pyz : float, optional
        The value to relax the yz shear pressure component to (default is
        0.0).
    tol : float, optional
        The relative tolerance used to determine if the lattice constants have
        converged (default is 1e-10).
    diverge_scale : float, optional
        Factor to identify if the system's dimensions have diverged.  Divergence
        is identified if either any current box dimension is greater than the
        original dimension multiplied by diverge_scale, or if any current box
        dimension is less than the original dimension divided by diverge_scale.
        (Default is 3.0).
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pxx = uc.set_in_units(pxx)
    pyy = uc.set_in_units(pyy)
    pzz = uc.set_in_units(pzz)
    pxy = uc.set_in_units(pxy)
    pxz = uc.set_in_units(pxz)
    pyz = uc.set_in_units(pyz)

    # Flag for if values have converged
    converged = False
    
    # Define current and old systems
    system_current = deepcopy(system)
    system_old = None
    
    # Save initial configuration as a dump file
    system.dump('atom_dump', f='initial.dump')
    
    for cycle in range(100):
        logfile = f'cij-{cycle}-log.lammps'

        # Run LAMMPS and evaluate results based on system_old
        results = cij_run0(lmp, system_current,
                           strainrange=strainrange,
                           logfile=logfile, usefiles=usefiles)
        
        system_new = update_box(system_current, results['C'], results['pij'],
                                pxx, pyy, pzz, pxy, pxz, pyz, tol)
        
        # Compare new and current to test for convergence
        if np.allclose(system_new.box.vects,
                       system_current.box.vects,
                       rtol=tol, atol=0):
            converged = True
            break
        
        # Compare old and new to test for double-value convergence
        elif system_old is not None and np.allclose(system_new.box.vects,
                                                    system_old.box.vects,
                                                    rtol=tol, atol=0):
            
            # Update current to average of old and new
            system_current.box_set(a = (system_new.box.a+system_old.box.a) / 2.,
                                   b = (system_new.box.b+system_old.box.b) / 2.,
                                   c = (system_new.box.c+system_old.box.c) / 2.,
                                   scale=True)
            
            # Calculate Cij for the averaged system
            results = cij_run0(lmp, system_current,
                               strainrange=strainrange,
                               logfile=logfile, usefiles=usefiles)
            system_new = update_box(system_current, results['C'], results['pij'],
                                    pxx, pyy, pzz, pxy, pxz, pyz, tol)
            converged = True
            break
        
        # Test for divergence
        elif system_new.box.a < system.box.a / diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.a > system.box.a * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.b < system.box.b / diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.b > system.box.b * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.c < system.box.c / diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.c > system.box.c * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif results['E_pot'] == 0.0:
            raise RuntimeError('Divergence: potential energy is 0')
        
        # If not converged or diverged, current -> old and new -> current
        else:
            system_old, system_current = system_current, system_new
    
    # Return values when converged
    if converged:
        system_new.dump('atom_dump', f='final.dump')
        
        # Build results_dict
        results_dict = {}
        results_dict['dumpfile_initial'] = 'initial.dump'
        results_dict['symbols_initial'] = system.symbols
        results_dict['dumpfile_final'] = 'final.dump'
        results_dict['symbols_final'] = system.symbols
        
        results_dict['lx'] = system_new.box.lx
        results_dict['ly'] = system_new.box.ly
        results_dict['lz'] = system_new.box.lz
        results_dict['xy'] = system_new.box.xy
        results_dict['xz'] = system_new.box.xz
        results_dict['yz'] = system_new.box.yz
        
        results_dict['E_pot'] = results['E_pot']
        results_dict['measured_pxx'] = results['pij'][0,0]
        results_dict['measured_pyy'] = results['pij'][1,1]
        results_dict['measured_pzz'] = results['pij'][2,2]
        results_dict['measured_pxy'] = results['pij'][0,1]
        results_dict['measured_pxz'] = results['pij'][0,2]
        results_dict['measured_pyz'] = results['pij'][1,2]
        
        return results_dict
    else:
        raise RuntimeError('Failed to converge after 100 cycles')

def cij_run0(lmp: LAMMPSobj,
             system: am.System,
             strainrange: float = 1e-6,
             logfile: Optional[str] = None,
             usefiles: bool = False) -> dict:
    """
    Runs cij_run0.in LAMMPS script to evaluate the elastic constants,
    pressure and potential energy of the current system.
    
    Parameters
    ----------
    lammps_command : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The system to perform the calculation on.
    strainrange : float, optional
        The small strain value to apply when calculating the elastic
        constants (default is 1e-6).
    logfile : int, optional
        Indicates the iteration cycle of quick_a_Cij().  This is used to
        uniquely save the LAMMPS input and output files.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_pot'** (*float*) - The potential energy per atom for the
          supplied system.
        - **'pressure'** (*numpy.array*) - The measured pressure state of the
          supplied system.
        - **'C_elastic'** (*atomman.ElasticConstants*) - The supplied system's
          elastic constants.
    """
    if usefiles:
        script = 'cij_run0'
    else:
        script = None
        logfile = 'none'
    
    thermo = []

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    # Specify strain
    lmp.cmd.variable('strain', 'equal', strainrange)

    # Specify variables of the initial configuration's dimensions
    lmp.cmd.variable('lx0', 'equal', '$(lx)')
    lmp.cmd.variable('ly0', 'equal', '$(ly)')
    lmp.cmd.variable('lz0', 'equal', '$(lz)')

    # Specify the thermo properties to calculate
    lmp.cmd.variable('peatom', 'equal', 'pe/atoms')

    # Define thermo info and integrator
    lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'yz', 'xz', 'xy', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'v_peatom', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    lmp.cmd.fix('nve', 'all', 'nve')

    # Run initial run0
    lmp.cmd.run(0)

    if lmp.islib and not usefiles:
        # Get thermo data
        thermo.append(lmp.last_thermo())
    else:
        # Define restart
        lmp.cmd.write_restart('initial.restart')

    shear_states = ['-x', '+x', '-y', '+y', '-z', '+z', 
                    '-yz', '+yz', '-xz', '+xz', '-xy', '+xy']
    for state in shear_states:

        # Reset system to the restart/original system
        lmp.new_system_from_restart(filename='initial.restart', system=system,
                                    tilt_large=True, usefiles=usefiles)

        # Redefine thermo info and integrator
        lmp.cmd.thermo_style('custom', 'step', 'lx', 'ly', 'lz', 'yz', 'xz', 'xy', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz', 'v_peatom', 'pe')
        lmp.cmd.thermo_modify('format', 'float', '%.17e')
        lmp.cmd.fix('nve', 'all', 'nve')

        # Apply the strain state
        add_strain(lmp, state)

        # Run strained run0
        lmp.cmd.run(0)

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

    # Convert units on thermo terms
    lmp.set_thermo_units(thermo)
    thermo.v_peatom = uc.set_in_units(thermo.v_peatom, lmp.unitsdict['energy'])

    return build_Cij_pij(thermo)

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

def build_Cij_pij(thermo):

    # Extract LAMMPS thermo data. Each term ranges i=0-12 where i=0 is undeformed
    # The remaining values are for -/+ strain pairs in the six unique directions
    lx = thermo.Lx.values
    ly = thermo.Ly.values
    lz = thermo.Lz.values
    xy = thermo.Xy.values
    xz = thermo.Xz.values
    yz = thermo.Yz.values
    
    pxx = thermo.Pxx.values
    pyy = thermo.Pyy.values
    pzz = thermo.Pzz.values
    pxy = thermo.Pxy.values
    pxz = thermo.Pxz.values
    pyz = thermo.Pyz.values
    
    pe = thermo.v_peatom
    
    # Extract the pressure tensor
    pij = np.array([[pxx[0], pxy[0], pxz[0]],
                    [pxy[0], pyy[0], pyz[0]],
                    [pxz[0], pyz[0], pzz[0]]])
    
    # Set the six non-zero strain values
    strains = np.array([ (lx[2] -  lx[1])  / lx[0],
                         (ly[4] -  ly[3])  / ly[0],
                         (lz[6] -  lz[5])  / lz[0],
                         (yz[8] -  yz[7])  / lz[0],
                         (xz[10] - xz[9])  / lz[0],
                         (xy[12] - xy[11]) / ly[0] ])
    
    # Calculate cij using stress changes associated with each non-zero strain
    cij = np.empty((6,6))
    for i in range(6):
        delta_stress = np.array([ pxx[2*i+1]-pxx[2*i+2],
                                  pyy[2*i+1]-pyy[2*i+2],
                                  pzz[2*i+1]-pzz[2*i+2],
                                  pyz[2*i+1]-pyz[2*i+2],
                                  pxz[2*i+1]-pxz[2*i+2],
                                  pxy[2*i+1]-pxy[2*i+2] ])
        
        cij[i] = delta_stress / strains[i] 
    
    for i in range(6):
        for j in range(i):
            cij[i,j] = cij[j,i] = (cij[i,j] + cij[j,i]) / 2
    
    C = am.ElasticConstants(Cij=cij)
    
    results = {}
    results['E_pot'] = pe[0]
    results['pij'] = pij
    results['C'] = C
    
    return results


def update_box(system: am.System,
               C: am.ElasticConstants,
               pij: np.ndarray,
               target_pxx: float = 0.0,
               target_pyy: float = 0.0,
               target_pzz: float = 0.0,
               target_pxy: float = 0.0,
               target_pxz: float = 0.0,
               target_pyz: float = 0.0,
               tol: float = 1e-10) -> am.System:
    """
    Generates a new system with an updated box that attempts to reach the target
    pressure. The new box dimensions are estimated by assuming linear elasticity
    and using the pressure and elastic constants of the current system.
    
    Parameters
    ----------
    system : atomman.System
        The system to update
    C : atomman.ElasticConstants
        The computed elastic constants for the system.
    pij : numpy.NDArray
        The 3x3 array of pressure tensors computed for the system.
    target_pxx : float, optional
        The value to relax the x tensile pressure component to. Default is
        0.0.
    target_pyy : float, optional
        The value to relax the y tensile pressure component to. Default is
        0.0.
    target_pzz : float, optional
        The value to relax the z tensile pressure component to. Default is
        0.0).
    target_pyz : float, optional
        The value to relax the yz shear pressure component to. Default is
        0.0).
    target_pxz : float, optional
        The value to relax the xz shear pressure component to. Default is
        0.0).
    target_pyz : float, optional
        The value to relax the xy shear pressure component to. Default is
        0.0).
    tol : float, optional
        The target tolerance.  Any strains less than this will be ignored.
        Default value is 1e-10.
        
    Returns
    -------
    atomman.System
        The System with updated box dimensions.
    """

    # Build the target pij array
    target_pij = np.array([[target_pxx, target_pxy, target_pxz],
                           [target_pxy, target_pyy, target_pyz],
                           [target_pxz, target_pyz, target_pzz]])
    
    # Adjust pij by the target
    pij = pij - target_pij
    
    # The stress state is the negative of the pressure state
    σij = -1 * pij
    
    # Compute the strain associated with the system relative to the target
    ϵij = np.einsum('ijkl,kl->ij', C.Sijkl, σij)
    ϵij[np.abs(ϵij) <= tol] = 0.0
    
    # Compute new box dimensions by removing the strain
    lx = system.box.lx - ϵij[0,0] * system.box.lx
    ly = system.box.ly - ϵij[1,1] * system.box.ly
    lz = system.box.lz - ϵij[2,2] * system.box.lz
    yz = system.box.yz - 2*ϵij[1,2] * system.box.lz
    xz = system.box.xz - 2*ϵij[0,2] * system.box.lz
    xy = system.box.xy - 2*ϵij[0,1] * system.box.ly

    if lx <= 0.0 or ly <= 0.0 or lz <= 0.0:
        raise RuntimeError('Divergence of box dimensions to <= 0')
    
    # Duplicate system and change dimensions
    system_new = deepcopy(system)
    system_new.box_set(lx=lx, ly=ly, lz=lz, yz=yz, xz=xz, xy=xy, scale=True)
    system_new.wrap()
    return system_new