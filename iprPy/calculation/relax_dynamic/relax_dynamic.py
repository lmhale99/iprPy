# Python script created by Lucas Hale and Karina Stetsyuk

# Standard library imports
import datetime
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def relax_dynamic(lammps_command: Union[str, LAMMPSobj],
                  system: am.System,
                  potential: lammpspotential,
                  mpi_command: Optional[str] = None,
                  pxx: unitfloat = 0.0,
                  pyy: unitfloat = 0.0,
                  pzz: unitfloat = 0.0,
                  pxy: unitfloat = 0.0,
                  pxz: unitfloat = 0.0,
                  pyz: unitfloat = 0.0,
                  temperature: float = 0.0,
                  integrator: Optional[str] = None,
                  equilsteps: int = 20000,
                  runsteps: int = 200000,
                  thermosteps: int = 100,
                  dumpsteps: Optional[int] = None,
                  restartsteps: Optional[int] = None,
                  createvelocities: bool = True,
                  randomseed: Optional[int] = None,
                  usefiles: bool = False) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
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
    pxx : float or str, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    pyy : float or str, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    pzz : float or str, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    pxy : float or str, optional
        The value to relax the xy shear pressure component to (default is
        0.0).
    pxz : float or str, optional
        The value to relax the xz shear pressure component to (default is
        0.0).
    pyz : float or str, optional
        The value to relax the yz shear pressure component to (default is
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
    logfile = 'log.lammps'
    restartfile = '*.restart'

    if usefiles:
        script = 'md_relax.in'
    else:
        script = None

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pxx = uc.set_in_units(pxx)
    pyy = uc.set_in_units(pyy)
    pzz = uc.set_in_units(pzz)
    pxy = uc.set_in_units(pxy)
    pxz = uc.set_in_units(pxz)
    pyz = uc.set_in_units(pyz)
    
    # Check temperature and set default integrator
    if temperature == 0.0:
        if integrator is None:
            integrator = 'nph+l'
        assert integrator not in ['npt', 'nvt'], 'npt and nvt cannot run at 0 K'
    elif temperature > 0:
        if integrator is None:
            integrator = 'npt'
    else:
        raise ValueError('Temperature must be positive')

    # Handle default values
    if dumpsteps is None:
        dumpsteps = runsteps
    if restartsteps is None:
        restartsteps = runsteps
    randomseed = am.lammps.seed(randomseed)
    
    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep
    pressure_damp = 1000 * timestep

    # Check if simulation is a restart
    isrestart = lmp.restart_check(logfile, restartfile)

    # Set up new simulation and run initial relaxations
    if not isrestart:

        # Pass system and potential info into LAMMPS
        lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                      usefiles=usefiles, logfile=logfile)
    
        # Set timestep
        lmp.cmd.timestep(timestep)

    else:
        # Tell LAMMPS to read in from restart and redefine potential
        lmp.new_system_from_restart(system, restartfile, tilt_large=True,
                                    usefiles=True, logfile=logfile)

    # Per-atom energy computes
    lmp.cmd.compute('pe', 'all', 'pe/atom')
    lmp.cmd.compute('ke', 'all', 'ke/atom')

    # Define thermo
    lmp.cmd.thermo(thermosteps)
    lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                         'lx', 'ly', 'lz', 'yz', 'xz', 'xy',
                         'pxx', 'pyy', 'pzz', 'pyz', 'pxz', 'pxy')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')

    # Create velocities
    if createvelocities:
        velocity_temperature = 2.0 * temperature + 1
        lmp.cmd.velocity('all', 'create', velocity_temperature, randomseed, 'mom',
                         'yes', 'rot', 'yes', 'dist', 'gaussian')


    # Integrator info
    if integrator == 'npt':
        lmp.cmd.fix('npt', 'all', 'npt',
                    'temp', temperature, temperature, temperature_damp,
                    'x', pxx, pxx, pressure_damp,
                    'y', pyy, pyy, pressure_damp,
                    'z', pzz, pzz, pressure_damp,
                    'xy', pxy, pxy, pressure_damp,
                    'xz', pxz, pxz, pressure_damp,
                    'yz', pyz, pyz, pressure_damp)

    elif integrator == 'nvt':
        lmp.cmd.fix('nvt', 'all', 'nvt',
                    'temp', temperature, temperature, temperature_damp)
    
    elif integrator == 'nph':
        lmp.cmd.fix('nph', 'all', 'nph',
                    'x', pxx, pxx, pressure_damp,
                    'y', pyy, pyy, pressure_damp,
                    'z', pzz, pzz, pressure_damp,
                    'xy', pxy, pxy, pressure_damp,
                    'xz', pxz, pxz, pressure_damp,
                    'yz', pyz, pyz, pressure_damp)
    
    elif integrator == 'nve':
        lmp.cmd.fix('nve', 'all', 'nve')
    
    elif integrator == 'nve+l':
        lmp.cmd.fix('nve', 'all', 'nve')
        lmp.cmd.fix('langevin', 'all', 'langevin',
                    temperature, temperature, temperature_damp, randomseed)

    elif integrator == 'nph+l':
        # Add ptemp if LAMMPS is newer than June 2020 and temperature is zero
        if np.isclose(temperature, 0.0) and lmp.versiondate >= datetime.date(2020, 6, 9):
            ptemp = ['ptemp', 1.0]
        else:
            ptemp = []
        
        lmp.cmd.fix('nph', 'all', 'nph',
                    'x', pxx, pxx, pressure_damp,
                    'y', pyy, pyy, pressure_damp,
                    'z', pzz, pzz, pressure_damp,
                    'xy', pxy, pxy, pressure_damp,
                    'xz', pxz, pxz, pressure_damp,
                    'yz', pyz, pyz, pressure_damp, *ptemp)
        lmp.cmd.fix('langevin', 'all', 'langevin',
                    temperature, temperature, temperature_damp, randomseed)
    
    else:
        raise ValueError('Invalid integrator style')


    # Equilibrium run
    if not isrestart:
        lmp.cmd.run(equilsteps)
        lmp.cmd.reset_timestep(0)

    # Dump configurations
    if lmp.potential.atom_style == 'charge':
        dump_keys = ['id', 'type', 'q', 'xu', 'yu', 'zu', 'c_pe', 'c_ke', 'vx', 'vy', 'vz']
    else:
        dump_keys = ['id', 'type', 'xu', 'yu', 'zu', 'c_pe', 'c_ke', 'vx', 'vy', 'vz']
    lmp.cmd.dump('dumpit', 'all', 'custom', dumpsteps, '*.dump', *dump_keys)
    lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')
    lmp.cmd.restart(restartsteps, restartfile)

    lmp.cmd.run(runsteps, 'upto')

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)
    
    # Get combined thermo data of primary simulation(s).
    thermo = log.flatten('last', firstindex=1).thermo
    lmp.set_thermo_units(thermo)
    
    results = {}
    results['dumpfile_initial'] = '0.dump'
    results['symbols_initial'] = system.symbols
    
    # Load relaxed system from dump file
    last_dump_file = f'{thermo.Step.values[-1]}.dump'
    results['dumpfile_final'] = last_dump_file
    system = am.load('atom_dump', last_dump_file, symbols=system.symbols)
    results['symbols_final'] = system.symbols
    
    # Get ave/stderr thermo properties
    nsamples = len(thermo)
    sqrt_nsamples = nsamples ** 0.5
    natoms = system.natoms
    
    # Energy estimates
    results['E_pot'] = thermo.PotEng.mean() / natoms
    results['E_pot_stderr'] = thermo.PotEng.std() / natoms / sqrt_nsamples
    results['E_total'] = thermo.TotEng.mean() / natoms
    results['E_total_stderr'] = thermo.TotEng.std() / natoms / sqrt_nsamples
    
    # Box dimension estimates
    results['lx'] = thermo.Lx.mean()
    results['lx_stderr'] = thermo.Lx.std() / sqrt_nsamples
    results['ly'] = thermo.Ly.mean()
    results['ly_stderr'] = thermo.Ly.std() / sqrt_nsamples
    results['lz'] = thermo.Lz.mean()
    results['lz_stderr'] = thermo.Lz.std() / sqrt_nsamples
    results['xy'] = thermo.Xy.mean()
    results['xy_stderr'] = thermo.Xy.std() / sqrt_nsamples
    results['xz'] = thermo.Xz.mean()
    results['xz_stderr'] = thermo.Xz.std() / sqrt_nsamples
    results['yz'] = thermo.Yz.mean()
    results['yz_stderr'] = thermo.Yz.std() / sqrt_nsamples
    
    # Pressure estimates
    results['measured_pxx'] = thermo.Pxx.mean()
    results['measured_pxx_stderr'] = thermo.Pxx.std() / sqrt_nsamples
    results['measured_pyy'] = thermo.Pyy.mean()
    results['measured_pyy_stderr'] = thermo.Pyy.std() / sqrt_nsamples
    results['measured_pzz'] = thermo.Pzz.mean()
    results['measured_pzz_stderr'] = thermo.Pzz.std() / sqrt_nsamples
    results['measured_pxy'] = thermo.Pxy.mean()
    results['measured_pxy_stderr'] = thermo.Pxy.std() / sqrt_nsamples
    results['measured_pxz'] = thermo.Pxz.mean()
    results['measured_pxz_stderr'] = thermo.Pxz.std() / sqrt_nsamples
    results['measured_pyz'] = thermo.Pyz.mean()
    results['measured_pyz_stderr'] = thermo.Pyz.std() / sqrt_nsamples
    
    # Temperature estimates
    results['temp'] = thermo.Temp.mean()
    results['temp_stderr'] = thermo.Temp.std() / sqrt_nsamples
    
    return results
