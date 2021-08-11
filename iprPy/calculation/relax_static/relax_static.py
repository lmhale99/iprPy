# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from copy import deepcopy
import shutil
from pathlib import Path
import datetime

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

def relax_static(lammps_command, system, potential, mpi_command=None,
                 p_xx=0.0, p_yy=0.0, p_zz=0.0, p_xy=0.0, p_xz=0.0, p_yz=0.0,
                 dispmult=0.0, etol=0.0, ftol=0.0,  maxiter=100000,
                 maxeval=1000000, dmax=uc.set_in_units(0.01, 'angstrom'),
                 maxcycles=100, ctol=1e-10):
    """
    Repeatedly runs the ELASTIC example distributed with LAMMPS until box
    dimensions converge within a tolerance.
    
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
    p_xx : float, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    p_yy : float, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    p_zz : float, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    p_xy : float, optional
        The value to relax the xy shear pressure component to (default is
        0.0).
    p_xz : float, optional
        The value to relax the xz shear pressure component to (default is
        0.0).
    p_yz : float, optional
        The value to relax the yz shear pressure component to (default is
        0.0).
    dispmult : float, optional
        Multiplier for applying a random displacement to all atomic positions
        prior to relaxing. Default value is 0.0.
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
    pressure_unit : str, optional
        The unit of pressure to calculate the elastic constants in (default is
        'GPa').
    maxcycles : int, optional
        The maximum number of times the minimization algorithm is called.
        Default value is 100.
    ctol : float, optional
        The relative tolerance used to determine if the lattice constants have
        converged (default is 1e-10).
    
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
        - **'measured_pxx'** (*float*) - The measured x tensile pressure
          component for the final configuration.
        - **'measured_pyy'** (*float*) - The measured y tensile pressure
          component for the final configuration.
        - **'measured_pzz'** (*float*) - The measured z tensile pressure
          component for the final configuration.
        - **'measured_pxy'** (*float*) - The measured xy shear pressure
          component for the final configuration.
        - **'measured_pxz'** (*float*) - The measured xz shear pressure
          component for the final configuration.
        - **'measured_pyz'** (*float*) - The measured yz shear pressure
          component for the final configuration.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Save initial configuration as a dump file
    system.dump('atom_dump', f='initial.dump')
    
    # Apply small random distortions to atoms
    system.atoms.pos += dispmult * np.random.rand(*system.atoms.pos.shape) - dispmult / 2
    
    # Initialize parameters
    old_vects = system.box.vects
    converged = False
    
    # Run minimizations up to maxcycles times
    for cycle in range(maxcycles):
        
        # Define lammps variables
        lammps_variables = {}
        system_info = system.dump('atom_data', f='init.dat',
                                  potential=potential)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        lammps_variables['p_xx'] = uc.get_in_units(p_xx, lammps_units['pressure'])
        lammps_variables['p_yy'] = uc.get_in_units(p_yy, lammps_units['pressure'])
        lammps_variables['p_zz'] = uc.get_in_units(p_zz, lammps_units['pressure'])
        lammps_variables['p_xy'] = uc.get_in_units(p_xy, lammps_units['pressure'])
        lammps_variables['p_xz'] = uc.get_in_units(p_xz, lammps_units['pressure'])
        lammps_variables['p_yz'] = uc.get_in_units(p_yz, lammps_units['pressure'])
        lammps_variables['etol'] = etol
        lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
        lammps_variables['maxiter'] = maxiter
        lammps_variables['maxeval'] = maxeval
        lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
        
        # Set dump_keys based on atom_style
        if potential.atom_style in ['charge']:
            lammps_variables['dump_keys'] = 'id type q x y z c_peatom'
        else:
            lammps_variables['dump_keys'] = 'id type x y z c_peatom'
        
        # Set dump_modify_format based on lammps_date
        if lammps_date < datetime.date(2016, 8, 3):
            if potential.atom_style in ['charge']:
                lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e"'
            else:
                lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
        else:
            lammps_variables['dump_modify_format'] = 'float %.13e'
        
        # Write lammps input script
        template_file = 'minbox.template'
        lammps_script = 'minbox.in'
        template = read_calc_file(parent_module, template_file)
        with open(lammps_script, 'w') as f:
            f.write(filltemplate(template, lammps_variables, '<', '>'))
        
        # Run LAMMPS and extract thermo data
        logfile = 'log-' + str(cycle) + '.lammps'
        output = lmp.run(lammps_command, lammps_script, mpi_command, logfile=logfile)
        thermo = output.simulations[0]['thermo']
        
        # Clean up dump files
        Path('0.dump').unlink()
        last_dump_file = str(thermo.Step.values[-1]) + '.dump'
        renamed_dump_file = 'relax_static-' + str(cycle) + '.dump'
        shutil.move(last_dump_file, renamed_dump_file)
        
        # Load relaxed system
        system = am.load('atom_dump', renamed_dump_file, symbols=system.symbols)
        
        # Test if box dimensions have converged
        if np.allclose(old_vects, system.box.vects, rtol=ctol, atol=0):
            converged = True
            break
        else:
            old_vects = system.box.vects
    
    # Check for convergence
    if converged is False:
        raise RuntimeError('Failed to converge after ' + str(maxcycles) + ' cycles')
    
    # Zero out near-zero tilt factors
    lx = system.box.lx
    ly = system.box.ly
    lz = system.box.lz
    xy = system.box.xy
    xz = system.box.xz
    yz = system.box.yz
    if np.isclose(xy/ly, 0.0, rtol=0.0, atol=1e-10):
        xy = 0.0
    if np.isclose(xz/lz, 0.0, rtol=0.0, atol=1e-10):
        xz = 0.0
    if np.isclose(yz/lz, 0.0, rtol=0.0, atol=1e-10):
        yz = 0.0
    system.box.set(lx=lx, ly=ly, lz=lz, xy=xy, xz=xz, yz=yz)
    system.wrap()
    
    # Build results_dict
    results_dict = {}
    results_dict['dumpfile_initial'] = 'initial.dump'
    results_dict['symbols_initial'] = system.symbols
    results_dict['dumpfile_final'] = renamed_dump_file
    results_dict['symbols_final'] = system.symbols
    results_dict['E_pot'] = uc.set_in_units(thermo.PotEng.values[-1] / system.natoms,
                                       lammps_units['energy'])
                                       
    results_dict['lx'] = uc.set_in_units(lx, lammps_units['length'])
    results_dict['ly'] = uc.set_in_units(ly, lammps_units['length'])
    results_dict['lz'] = uc.set_in_units(lz, lammps_units['length'])
    results_dict['xy'] = uc.set_in_units(xy, lammps_units['length'])
    results_dict['xz'] = uc.set_in_units(xz, lammps_units['length'])
    results_dict['yz'] = uc.set_in_units(yz, lammps_units['length'])
    
    results_dict['measured_pxx'] = uc.set_in_units(thermo.Pxx.values[-1],
                                                   lammps_units['pressure'])
    results_dict['measured_pyy'] = uc.set_in_units(thermo.Pyy.values[-1],
                                                   lammps_units['pressure'])
    results_dict['measured_pzz'] = uc.set_in_units(thermo.Pzz.values[-1],
                                                   lammps_units['pressure'])
    results_dict['measured_pxy'] = uc.set_in_units(thermo.Pxy.values[-1],
                                                   lammps_units['pressure'])
    results_dict['measured_pxz'] = uc.set_in_units(thermo.Pxz.values[-1],
                                                   lammps_units['pressure'])
    results_dict['measured_pyz'] = uc.set_in_units(thermo.Pyz.values[-1],
                                                   lammps_units['pressure'])
    
    return results_dict
