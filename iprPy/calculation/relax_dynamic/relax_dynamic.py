# coding: utf-8

# Python script created by Lucas Hale and Karina Stetsyuk

# Standard library imports
import datetime
import random
from typing import Optional

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

import numpy as np

# iprPy imports
from ...tools import read_calc_file

def relax_dynamic(lammps_command: str,
                  system: am.System,
                  potential: lmp.Potential,
                  mpi_command: Optional[str] = None,
                  p_xx: float = 0.0,
                  p_yy: float = 0.0,
                  p_zz: float = 0.0,
                  p_xy: float = 0.0,
                  p_xz: float = 0.0,
                  p_yz: float = 0.0,
                  temperature: float = 0.0,
                  integrator: Optional[str] = None,
                  runsteps: int = 220000,
                  thermosteps: int = 100,
                  dumpsteps: Optional[int] = None,
                  restartsteps: Optional[int] = None,
                  equilsteps: int = 20000,
                  randomseed: Optional[int] = None) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
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
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    runsteps : int, optional
        The number of integration steps to perform (default is 220000).
    integrator : str or None, optional
        The integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
        (Default is None, which will use 'nph+l' for temperature == 0, and
        'npt' otherwise.)
    thermosteps : int, optional
        Thermo values will be reported every this many steps (default is
        100).
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps (default is None,
        which sets dumpsteps equal to runsteps).
    restartsteps : int or None, optional
        Restart files will be saved every this many steps (default is None,
        which sets restartsteps equal to runsteps).
    equilsteps : int, optional
        The number of timesteps at the beginning of the simulation to
        exclude when computing average values (default is 20000).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    
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
        - **'nsamples'** (*int*) - The number of thermodynamic samples included
          in the mean and standard deviation estimates.  Can also be used to
          estimate standard error values assuming that the thermo step size is
          large enough (typically >= 100) to assume the samples to be
          independent.
        - **'E_pot'** (*float*) - The mean measured potential energy.
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
        - **'temp'** (*float*) - The mean measured temperature.
        - **'E_pot_std'** (*float*) - The standard deviation in the measured
          potential energy values.
        - **'measured_pxx_std'** (*float*) - The standard deviation in the
          measured x tensile pressure of the relaxed system.
        - **'measured_pyy_std'** (*float*) - The standard deviation in the
          measured y tensile pressure of the relaxed system.
        - **'measured_pzz_std'** (*float*) - The standard deviation in the
          measured z tensile pressure of the relaxed system.
        - **'measured_pxy_std'** (*float*) - The standard deviation in the
          measured xy shear pressure of the relaxed system.
        - **'measured_pxz_std'** (*float*) - The standard deviation in the
          measured xz shear pressure of the relaxed system.
        - **'measured_pyz_std'** (*float*) - The standard deviation in the
          measured yz shear pressure of the relaxed system.
        - **'temp_std'** (*float*) - The standard deviation in the measured
          temperature values.
    """
  
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Handle default values
    if dumpsteps is None:
        dumpsteps = runsteps
    if restartsteps is None:
        restartsteps = runsteps
    
    # Define lammps variables
    lammps_variables = {}
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Generate LAMMPS inputs for restarting
    system_info2 = potential.pair_restart_info('*.restart', system.symbols)
    lammps_variables['atomman_pair_restart_info'] = system_info2
    
    # Integrator lines for main run
    integ_info = integrator_info(integrator=integrator,
                                 p_xx=p_xx, p_yy=p_yy, p_zz=p_zz,
                                 p_xy=p_xy, p_xz=p_xz, p_yz=p_yz,
                                 temperature=temperature,
                                 randomseed=randomseed,
                                 units=potential.units,
                                 lammps_date=lammps_date)
    lammps_variables['integrator_info'] = integ_info

    # Integrator lines for restarts
    integ_info2 = integrator_info(integrator=integrator,
                                 p_xx=p_xx, p_yy=p_yy, p_zz=p_zz,
                                 p_xy=p_xy, p_xz=p_xz, p_yz=p_yz,
                                 temperature=temperature,
                                 velocity_temperature=0.0,
                                 randomseed=randomseed,
                                 units=potential.units,
                                 lammps_date=lammps_date)
    lammps_variables['integrator_restart_info'] = integ_info2

    # Other run settings
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['restartsteps'] = restartsteps
    
    # Set dump_keys based on atom_style
    if potential.atom_style in ['charge']:
        lammps_variables['dump_keys'] = 'id type q xu yu zu c_pe c_ke'
    else:
        lammps_variables['dump_keys'] = 'id type xu yu zu c_pe c_ke'

    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        if potential.atom_style in ['charge']:
            lammps_variables['dump_modify_format'] = f'"%d %d{12 * " %.13e"}"'
        else:
            lammps_variables['dump_modify_format'] = f'"%d %d{11 * " %.13e"}"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    lammps_script = 'full_relax.in'
    template = read_calc_file('iprPy.calculation.relax_dynamic',
                              'full_relax.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Write lammps restart input script
    restart_script = 'full_relax_restart.in'
    template = read_calc_file('iprPy.calculation.relax_dynamic',
                              'full_relax_restart.template')
    with open(restart_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, script_name=lammps_script,
                     restart_script_name=restart_script,
                     mpi_command=mpi_command, screen=False)
    
    # Extract LAMMPS thermo data. 
    results = {}
    thermo = output.flatten()['thermo']
    
    results['dumpfile_initial'] = '0.dump'
    results['symbols_initial'] = system.symbols
    
    # Load relaxed system from dump file
    last_dump_file = f'{thermo.Step.values[-1]}.dump'
    results['dumpfile_final'] = last_dump_file
    system = am.load('atom_dump', last_dump_file, symbols=system.symbols)
    results['symbols_final'] = system.symbols
    
    # Only consider values where Step >= equilsteps
    thermo = thermo[thermo.Step >= equilsteps]
    results['nsamples'] = len(thermo)
    
    # Get cohesive energy estimates
    natoms = system.natoms
    results['E_pot'] = uc.set_in_units(thermo.PotEng.mean() / natoms, lammps_units['energy'])
    results['E_pot_std'] = uc.set_in_units(thermo.PotEng.std() / natoms, lammps_units['energy'])

    results['E_total'] = uc.set_in_units(thermo.TotEng.mean() / natoms, lammps_units['energy'])
    results['E_total_std'] = uc.set_in_units(thermo.TotEng.std() / natoms, lammps_units['energy'])
    
    results['lx'] = uc.set_in_units(thermo.Lx.mean(), lammps_units['length'])
    results['lx_std'] = uc.set_in_units(thermo.Lx.std(), lammps_units['length'])
    results['ly'] = uc.set_in_units(thermo.Ly.mean(), lammps_units['length'])
    results['ly_std'] = uc.set_in_units(thermo.Ly.std(), lammps_units['length'])
    results['lz'] = uc.set_in_units(thermo.Lz.mean(), lammps_units['length'])
    results['lz_std'] = uc.set_in_units(thermo.Lz.std(), lammps_units['length'])
    results['xy'] = uc.set_in_units(thermo.Xy.mean(), lammps_units['length'])
    results['xy_std'] = uc.set_in_units(thermo.Xy.std(), lammps_units['length'])
    results['xz'] = uc.set_in_units(thermo.Xz.mean(), lammps_units['length'])
    results['xz_std'] = uc.set_in_units(thermo.Xz.std(), lammps_units['length'])
    results['yz'] = uc.set_in_units(thermo.Yz.mean(), lammps_units['length'])
    results['yz_std'] = uc.set_in_units(thermo.Yz.std(), lammps_units['length'])
    
    results['measured_pxx'] = uc.set_in_units(thermo.Pxx.mean(), lammps_units['pressure'])
    results['measured_pxx_std'] = uc.set_in_units(thermo.Pxx.std(), lammps_units['pressure'])
    results['measured_pyy'] = uc.set_in_units(thermo.Pyy.mean(), lammps_units['pressure'])
    results['measured_pyy_std'] = uc.set_in_units(thermo.Pyy.std(), lammps_units['pressure'])
    results['measured_pzz'] = uc.set_in_units(thermo.Pzz.mean(), lammps_units['pressure'])
    results['measured_pzz_std'] = uc.set_in_units(thermo.Pzz.std(), lammps_units['pressure'])
    results['measured_pxy'] = uc.set_in_units(thermo.Pxy.mean(), lammps_units['pressure'])
    results['measured_pxy_std'] = uc.set_in_units(thermo.Pxy.std(), lammps_units['pressure'])
    results['measured_pxz'] = uc.set_in_units(thermo.Pxz.mean(), lammps_units['pressure'])
    results['measured_pxz_std'] = uc.set_in_units(thermo.Pxz.std(), lammps_units['pressure'])
    results['measured_pyz'] = uc.set_in_units(thermo.Pyz.mean(), lammps_units['pressure'])
    results['measured_pyz_std'] = uc.set_in_units(thermo.Pyz.std(), lammps_units['pressure'])
    results['temp'] = thermo.Temp.mean()
    results['temp_std'] = thermo.Temp.std()
    
    return results

def integrator_info(integrator: Optional[str] = None, 
                    p_xx: float = 0.0,
                    p_yy: float = 0.0,
                    p_zz: float = 0.0,
                    p_xy: float = 0.0,
                    p_xz: float = 0.0,
                    p_yz: float = 0.0,
                    temperature: float = 0.0,
                    velocity_temperature: Optional[float] = None,
                    randomseed: Optional[int] = None,
                    units: str = 'metal',
                    lammps_date=None) -> str:
    """
    Generates LAMMPS commands for velocity creation and fix integrators. 
    
    Parameters
    ----------
    integrator : str or None, optional
        The integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
        (Default is None, which will use 'nph+l' for temperature == 0, and
        'npt' otherwise.)
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
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    velocity_temperature : float or None, optional
        The temperature to use for generating initial atomic velocities with
        integrators containing thermostats.  If None (default) then it will
        be set to 2 * temperature + 1.  If 0.0 then the velocities will not be
        (re)set.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    units : str, optional
        The LAMMPS units style to use (default is 'metal').
    
    Returns
    -------
    str
        The generated LAMMPS input lines for velocity create and fix
        integration commands.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(units)

    # Convert pressures to lammps units
    p_xx = uc.get_in_units(p_xx, lammps_units['pressure'])
    p_yy = uc.get_in_units(p_yy, lammps_units['pressure'])
    p_zz = uc.get_in_units(p_zz, lammps_units['pressure'])
    p_xy = uc.get_in_units(p_xy, lammps_units['pressure'])
    p_xz = uc.get_in_units(p_xz, lammps_units['pressure'])
    p_yz = uc.get_in_units(p_yz, lammps_units['pressure'])

    # Check temperature and set default integrator
    if temperature == 0.0:
        if integrator is None: integrator = 'nph+l'
        assert integrator not in ['npt', 'nvt'], 'npt and nvt cannot run at 0 K'
    elif temperature > 0:
        if integrator is None: integrator = 'npt'
    else:
        raise ValueError('Temperature must be positive')
    
    # Set dampening parameters based on timestep values
    temperature_damp = 100 * lmp.style.timestep(units)
    pressure_damp = 1000 * lmp.style.timestep(units)

    # Set default randomseed
    if randomseed is None: 
        randomseed = random.randint(1, 900000000)
    
    # Set default velocity_temperature
    if velocity_temperature is None:
        velocity_temperature = 2.0 * temperature + 1

    # Build info_lines
    info_lines = []

    if integrator == 'npt':

        if velocity_temperature > 0.0:
            info_lines.append(f'velocity all create {velocity_temperature} {randomseed}')

        info_lines.extend([
            f'fix npt all npt temp {temperature} {temperature} {temperature_damp} &',
            f'                x {p_xx} {p_xx} {pressure_damp} &',
            f'                y {p_yy} {p_yy} {pressure_damp} &',
            f'                z {p_zz} {p_zz} {pressure_damp} &',
            f'                xy {p_xy} {p_xy} {pressure_damp} &',
            f'                xz {p_xz} {p_xz} {pressure_damp} &',
            f'                yz {p_yz} {p_yz} {pressure_damp}'
        ])

    
    elif integrator == 'nvt':
        
        if velocity_temperature > 0.0:
            info_lines.append(f'velocity all create {velocity_temperature} {randomseed}')
        
        info_lines.extend([
            f'fix nvt all nvt temp {temperature} {temperature} {temperature_damp}'
        ])
    
    elif integrator == 'nph':

        info_lines.extend([
            f'fix nph all nph x {p_xx} {p_xx} {pressure_damp} &',
            f'                y {p_yy} {p_yy} {pressure_damp} &',
            f'                z {p_zz} {p_zz} {pressure_damp} &',
            f'                xy {p_xy} {p_xy} {pressure_damp} &',
            f'                xz {p_xz} {p_xz} {pressure_damp} &',
            f'                yz {p_yz} {p_yz} {pressure_damp}'
        ])
    
    elif integrator == 'nve':
        
        info_lines.extend([
            'fix nve all nve'
        ])
        
    elif integrator == 'nve+l':

        if velocity_temperature > 0.0:
            info_lines.append(f'velocity all create {velocity_temperature} {randomseed}')

        info_lines.extend([
            'fix nve all nve',
            f'fix langevin all langevin {temperature} {temperature} {temperature_damp} {randomseed}'
        ])

    elif integrator == 'nph+l':

        info_lines.extend([
            f'fix nph all nph x {p_xx} {p_xx} {pressure_damp} &',
            f'                y {p_yy} {p_yy} {pressure_damp} &',
            f'                z {p_zz} {p_zz} {pressure_damp} &',
            f'                xy {p_xy} {p_xy} {pressure_damp} &',
            f'                xz {p_xz} {p_xz} {pressure_damp} &',
            f'                yz {p_yz} {p_yz} {pressure_damp}',
        ])
        
        # Add ptemp if LAMMPS is newer than June 2020 and temperature is zero
        if np.isclose(temperature, 0.0) and lammps_date >= datetime.date(2020, 6, 9):
            info_lines[-1] += ' &'
            info_lines.extend(['                ptemp 1.0'])
            
        info_lines.extend([f'fix langevin all langevin {temperature} {temperature} {temperature_damp} {randomseed}'])
    
    else:
        raise ValueError('Invalid integrator style')
    
    return '\n'.join(info_lines)
