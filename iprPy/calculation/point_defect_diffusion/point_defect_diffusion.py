# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential
from atomman.lammps import LAMMPS, LAMMPSobj

def pointdiffusion(lammps_command: Union[str, LAMMPSobj],
                   system: am.System,
                   potential: lammpspotential,
                   point_kwargs: Union[list, dict],
                   mpi_command: Optional[str] = None,
                   temperature: float = 300.0,
                   runsteps: int = 200000,
                   thermosteps: Optional[int] = None,
                   dumpsteps: int = 0,
                   equilsteps: int = 20000,
                   randomseed: Optional[int] = None,
                   usefiles: bool = False) -> dict:
    """
    Evaluates the diffusion rate of a point defect at a given temperature. This
    method will run two simulations: an NVT run at the specified temperature to 
    equilibrate the system, then an NVE run to measure the defect's diffusion 
    rate. The diffusion rate is evaluated using the mean squared displacement of
    all atoms in the system, and using the assumption that diffusion is only due
    to the added defect(s).
    
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
    temperature : float, optional
        The temperature to run at (default is 300.0).
    runsteps : int, optional
        The number of integration steps to perform (default is 200000).
    thermosteps : int, optional
        Thermo values will be reported every this many steps (default is
        runsteps divided by 1000).
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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'diffusion.in'
    else:
        script = None

    # Handle default values
    if thermosteps is None: 
        thermosteps = runsteps // 1000
        if thermosteps == 0:
            thermosteps = 1
    if dumpsteps is None:
        dumpsteps = runsteps

    # Check/select a randomseed value
    randomseed = am.lammps.seed(randomseed)

    # Check that temperature is greater than zero
    if temperature <= 0.0:
        raise ValueError('Temperature must be greater than zero')

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep

    # Add defect(s) to the initially perfect system
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        #print(pkwargs)
        system = am.defect.point(system, **pkwargs)
    
    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('\n# Specify property computes')
    lmp.cmd.compute('peatom', 'all', 'pe/atom')
    lmp.cmd.compute('msd', 'all', 'msd', 'com', 'yes')

    lmp.commands_string('\n# Define thermo data')
    lmp.cmd.thermo(thermosteps)
    lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                         'pxx', 'pyy', 'pzz', 'c_msd[1]', 'c_msd[2]', 'c_msd[3]', 'c_msd[4]')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    lmp.commands_string('\n# Specify timestep')
    lmp.cmd.timestep(timestep)

    lmp.commands_string('\n# Create velocities and equilibrate system using nvt')
    lmp.cmd.velocity('all', 'create', 2*temperature, randomseed)
    lmp.cmd.fix('nvt', 'all', 'nvt', 'temp', temperature, temperature, temperature_damp)
    lmp.cmd.run(equilsteps)
    lmp.cmd.unfix('nvt')
    
    if dumpsteps > 0:
        lmp.commands_string('\n# Define dump')
        if lmp.potential.atom_style == 'charge':
            dumpkeys = ['id', 'type', 'q', 'x', 'y', 'z', 'c_peatom']
        else:
            dumpkeys = ['id', 'type', 'x', 'y', 'z', 'c_peatom']
        lmp.cmd.dump('dumpit', 'all', 'custom', dumpsteps, '*.dump', *dumpkeys)
        lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')

    lmp.commands_string('\n# Run nve')
    lmp.cmd.reset_timestep(0)
    lmp.cmd.fix('nve', 'all', 'nve')
    lmp.cmd.run(runsteps)

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
    
    # Extract LAMMPS thermo data and auto-set standard thermo units
    thermo = log.simulations[1]['thermo']
    lmp.set_thermo_units(thermo)

    temps = thermo.Temp.values
    pxxs = thermo.Pxx.values
    pyys = thermo.Pyy.values
    pzzs = thermo.Pzz.values
    E_pots = thermo.PotEng.values
    E_totals = thermo.TotEng.values
    steps = thermo.Step.values
    
    # Read user-defined thermo data
    mds_units = f"{lmp.unitsdict['length']}^2"
    msd_x = uc.set_in_units(thermo['c_msd[1]'].values, mds_units)
    msd_y = uc.set_in_units(thermo['c_msd[2]'].values, mds_units)
    msd_z = uc.set_in_units(thermo['c_msd[3]'].values, mds_units)
    msd = uc.set_in_units(thermo['c_msd[4]'].values, mds_units)
        
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
    
    # Convert steps to time values
    t = steps * uc.set_in_units(timestep, lmp.unitsdict['time'])
    
    # Estimate diffusion rates
    # MSD_ptd = natoms * MSD_atoms (if one defect in system)
    # MSD = 2 * ndim * D * t  -->  D = MSD/t / (2 * ndim)
    mx = np.polyfit(t, system.natoms * msd_x, 1)[0]
    my = np.polyfit(t, system.natoms * msd_y, 1)[0]
    mz = np.polyfit(t, system.natoms * msd_z, 1)[0]
    m = np.polyfit(t, system.natoms * msd, 1)[0]
    
    results['msd_x_values'] = msd_x
    results['msd_y_values'] = msd_y
    results['msd_z_values'] = msd_z
    results['msd_values'] = msd
    results['dx'] = mx / 2
    results['dy'] = my / 2
    results['dz'] = mz / 2
    results['d'] = m / 6
    
    return results
