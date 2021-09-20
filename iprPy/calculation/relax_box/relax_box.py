# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from ...tools import filltemplate, read_calc_file

# Define calculation metadata
parent_module = '.'.join(__name__.split('.')[:-1])

def relax_box(lammps_command, system, potential,
              mpi_command=None, strainrange=1e-6,
              pxx=0.0, pyy=0.0, pzz=0.0, pxy=0.0, pxz=0.0, pyz=0.0,
              tol=1e-10, diverge_scale=3.):
    """
    Quickly refines static orthorhombic system by evaluating the elastic
    constants and the virial pressure.
    
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
        - **'measured_pij'** (*float*) - The measured pressure tensor
          for the final configuration.
    
    Raises
    ------
    RuntimeError
        If system diverges or no convergence reached after 100 cycles.
    """
    
    # Flag for if values have converged
    converged = False
    
    # Define current and old systems
    system_current = deepcopy(system)
    system_old = None
    
    system.dump('atom_dump', f='initial.dump')
    
    for cycle in range(100):
        
        # Run LAMMPS and evaluate results based on system_old
        results = cij_run0(lammps_command, system_current, potential,
                           mpi_command=mpi_command, strainrange=strainrange,
                           cycle=cycle)
        pij = results['pij']
        Cij = results['C'].Cij
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
            results = cij_run0(lammps_command, system_current, potential,
                               mpi_command=mpi_command, strainrange=strainrange,
                               cycle=cycle)
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
        results_dict['measured_pij'] = results['pij']
        
        return results_dict
    else:
        raise RuntimeError('Failed to converge after 100 cycles')

def cij_run0(lammps_command, system, potential, mpi_command=None,
             strainrange=1e-6, cycle=0):
    """
    Runs cij_run0.in LAMMPS script to evaluate the elastic constants,
    pressure and potential energy of the current system.
    
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
    cycle : int, optional
        Indicates the iteration cycle of quick_a_Cij().  This is used to
        uniquely save the LAMMPS input and output files.
    
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

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    restart_info = potential.pair_restart_info('initial.restart', system.symbols)
    lammps_variables['pair_data_info'] = system_info
    lammps_variables['pair_restart_info'] = restart_info
    lammps_variables['strainrange'] = strainrange
    
    # Write lammps input script
    template_file = 'cij_run0.template'
    lammps_script = 'cij_run0.in'
    template = read_calc_file(parent_module, template_file)
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command,
                     logfile=f'cij-{cycle}-log.lammps')
    thermo = output.flatten('all').thermo
    
    # Extract LAMMPS thermo data. Each term ranges i=0-12 where i=0 is undeformed
    # The remaining values are for -/+ strain pairs in the six unique directions
    lx = uc.set_in_units(thermo.Lx, lammps_units['length'])
    ly = uc.set_in_units(thermo.Ly, lammps_units['length'])
    lz = uc.set_in_units(thermo.Lz, lammps_units['length'])
    xy = uc.set_in_units(thermo.Xy, lammps_units['length'])
    xz = uc.set_in_units(thermo.Xz, lammps_units['length'])
    yz = uc.set_in_units(thermo.Yz, lammps_units['length'])
    
    pxx = uc.set_in_units(thermo.Pxx, lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy, lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz, lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy, lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz, lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz, lammps_units['pressure'])
    
    pe = uc.set_in_units(thermo.PotEng / system.natoms, lammps_units['energy'])
    
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
    
def update_box(system, C, pij, target_pxx=0.0, target_pyy=0.0, target_pzz=0.0, 
               target_pxy=0.0, target_pxz=0.0, target_pyz=0.0, tol=1e-10):    
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