# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from copy import deepcopy
import shutil
import datetime
import random

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

def pointdiffusion(lammps_command, system, potential, point_kwargs,
                   mpi_command=None, temperature=300,
                   runsteps=200000, thermosteps=None, dumpsteps=0,
                   equilsteps=20000, randomseed=None):
                   
    """
    Evaluates the diffusion rate of a point defect at a given temperature. This
    method will run two simulations: an NVT run at the specified temperature to 
    equilibrate the system, then an NVE run to measure the defect's diffusion 
    rate. The diffusion rate is evaluated using the mean squared displacement of
    all atoms in the system, and using the assumption that diffusion is only due
    to the added defect(s).
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    temperature : float, optional
        The temperature to run at (default is 300.0).
    runsteps : int, optional
        The number of integration steps to perform (default is 200000).
    thermosteps : int, optional
        Thermo values will be reported every this many steps (default is
        100).
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps (default is 0,
        which does not output dump files).
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
        
        - **'natoms'** (*int*) - The number of atoms in the system.
        - **'temp'** (*float*) - The mean measured temperature.
        - **'pxx'** (*float*) - The mean measured normal xx pressure.
        - **'pyy'** (*float*) - The mean measured normal yy pressure.
        - **'pzz'** (*float*) - The mean measured normal zz pressure.
        - **'Epot'** (*numpy.array*) - The mean measured total potential 
          energy.
        - **'temp_std'** (*float*) - The standard deviation in the measured
          temperature values.
        - **'pxx_std'** (*float*) - The standard deviation in the measured
          normal xx pressure values.
        - **'pyy_std'** (*float*) - The standard deviation in the measured
          normal yy pressure values.
        - **'pzz_std'** (*float*) - The standard deviation in the measured
          normal zz pressure values.
        - **'Epot_std'** (*float*) - The standard deviation in the measured
          total potential energy values.
        - **'dx'** (*float*) - The computed diffusion constant along the 
          x-direction.
        - **'dy'** (*float*) - The computed diffusion constant along the 
          y-direction.
        - **'dz'** (*float*) - The computed diffusion constant along the 
          y-direction.
        - **'d'** (*float*) - The total computed diffusion constant.
    """

    # Add defect(s) to the initially perfect system
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        #print(pkwargs)
        system = am.defect.point(system, **pkwargs)
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Check that temperature is greater than zero
    if temperature <= 0.0:
        raise ValueError('Temperature must be greater than zero')
    
    # Handle default values
    if thermosteps is None: 
        thermosteps = runsteps // 1000
        if thermosteps == 0:
            thermosteps = 1
    if dumpsteps is None:
        dumpsteps = runsteps
    if randomseed is None:
        randomseed = random.randint(1, 900000000)
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='perfect.dat',
                              potential=potential,
                              return_pair_info=True)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['temperature'] = temperature
    lammps_variables['runsteps'] = runsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['randomseed'] = randomseed
    lammps_variables['timestep'] = lmp.style.timestep(potential.units)
    
    # Set dump_info
    if dumpsteps == 0:
        lammps_variables['dump_info'] = ''
    else:
        lammps_variables['dump_info'] = '\n'.join([
            '',
            '# Define dump files',
            'dump dumpit all custom ${dumpsteps} *.dump id type x y z c_peatom',
            'dump_modify dumpit format <dump_modify_format>',
            '',
        ])
        
        # Set dump_modify_format based on lammps_date
        if lammps_date < datetime.date(2016, 8, 3):
            lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
        else:
            lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = 'diffusion.template'
    lammps_script = 'diffusion.in'
    template = read_calc_file(parent_module, template_file)
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract LAMMPS thermo data.
    thermo = output.simulations[1]['thermo']
    temps = thermo.Temp.values
    pxxs = uc.set_in_units(thermo.Pxx.values, lammps_units['pressure'])
    pyys = uc.set_in_units(thermo.Pyy.values, lammps_units['pressure'])
    pzzs = uc.set_in_units(thermo.Pzz.values, lammps_units['pressure'])
    E_pots = uc.set_in_units(thermo.PotEng.values, lammps_units['energy'])
    E_totals = uc.set_in_units(thermo.TotEng.values, lammps_units['energy'])
    steps = thermo.Step.values
    
    # Read user-defined thermo data
    if output.lammps_date < datetime.date(2016, 8, 1):
        msd_x = uc.set_in_units(thermo['msd[1]'].values,
                                lammps_units['length']+'^2')
        msd_y = uc.set_in_units(thermo['msd[2]'].values,
                                lammps_units['length']+'^2')
        msd_z = uc.set_in_units(thermo['msd[3]'].values,
                                lammps_units['length']+'^2')
        msd = uc.set_in_units(thermo['msd[4]'].values,
                              lammps_units['length']+'^2')
    else:
        msd_x = uc.set_in_units(thermo['c_msd[1]'].values,
                                lammps_units['length']+'^2')
        msd_y = uc.set_in_units(thermo['c_msd[2]'].values,
                                lammps_units['length']+'^2')
        msd_z = uc.set_in_units(thermo['c_msd[3]'].values,
                                lammps_units['length']+'^2')
        msd = uc.set_in_units(thermo['c_msd[4]'].values,
                              lammps_units['length']+'^2')
        
    # Initialize results dict
    results = {}
    results['natoms'] = system.natoms
    results['nsamples'] = len(thermo)
    
    # Get mean and std for temperature, pressure, and energy
    results['temp'] = np.mean(temps)
    results['temp_std'] = np.std(temps)
    results['pxx'] = np.mean(pxxs)
    results['pxx_std'] = np.std(pxxs)
    results['pyy'] = np.mean(pyys)
    results['pyy_std'] = np.std(pyys)
    results['pzz'] = np.mean(pzzs)
    results['pzz_std'] = np.std(pzzs)
    results['E_pot'] = np.mean(E_pots)
    results['E_pot_std'] = np.std(E_pots)
    results['E_total'] = np.mean(E_totals)
    results['E_total_std'] = np.std(E_totals)
    
    # Convert steps to times
    times = steps * uc.set_in_units(lammps_variables['timestep'], lammps_units['time'])
    
    # Estimate diffusion rates
    # MSD_ptd = natoms * MSD_atoms (if one defect in system)
    # MSD = 2 * ndim * D * t  -->  D = MSD/t / (2 * ndim)
    mx = np.polyfit(times, system.natoms * msd_x, 1)[0]
    my = np.polyfit(times, system.natoms * msd_y, 1)[0]
    mz = np.polyfit(times, system.natoms * msd_z, 1)[0]
    m = np.polyfit(times, system.natoms * msd, 1)[0]
    
    results['dx'] = mx / 2
    results['dy'] = my / 2
    results['dz'] = mz / 2
    results['d'] = m / 6
    
    return results

