# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
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

def relax_liquid(lammps_command: str,
                 system: am.System,
                 potential: lmp.Potential,
                 temperature: float,
                 mpi_command: Optional[str] = None,
                 pressure: float = 0.0,
                 temperature_melt: float = 3000.0,
                 rdfcutoff: Optional[float] = None,
                 meltsteps: int = 50000,
                 coolsteps: int = 10000,
                 equilvolumesteps: int = 50000,
                 equilvolumesamples: int = 300,
                 equilenergysteps: int = 10000,
                 equilenergysamples: int = 100,
                 equilenergystyle: str = 'pe',
                 runsteps: int = 50000,
                 dumpsteps: Optional[int] = None,
                 restartsteps: Optional[int] = None,
                 createvelocities: bool = True,
                 randomseed: Optional[int] = None) -> dict:
    """
    Performs a multi-stage simulation to obtain a liquid phase configuration 
    at a given temperature. Radial displacement functions and mean squared
    displacements are automatically computed for the system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature : float
        The target temperature to relax to.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    pressure : float, optional
        The target hydrostatic pressure to relax to. Default value is 0. GPa.
    temperature_melt : float, optional
        The elevated temperature to first use to hopefully melt the initial
        configuration.
    rdfcutoff : float, optional
        The cutoff distance to use for the RDF cutoff.  If not given then
        will use 4 * r0, where r0 is the shortest atomic distance found in
        the given system configuration.
    meltsteps : int, optional
        The number of npt integration steps to perform during the melting
        stage at the melt temperature to create an amorphous liquid structure.
        Default value is 50000.
    coolsteps : int, optional
        The number of npt integration steps to perform during the cooling
        stage where the temperature is reduced from the melt temperature
        to the target temperature.  Default value is 10000.
    equilvolumesteps : int, optional
        The number of npt integration steps to perform during the volume
        equilibration stage where the system is held at the target temperature
        and pressure to obtain an estimate for the relaxed volume.  Default
        value is 50000.
    equilvolumesamples : int, optional
        The number of thermo samples from the end of the volume equilibration
        stage to use in computing the average volume.  Cannot be larger than
        equilvolumesteps / 100.  It is recommended to set smaller than the max
        to allow for some convergence time.  Default value is 300. 
    equilenergysteps : int, optional
        The number of nvt integration steps to perform during the energy
        equilibration stage where the system is held at the target temperature
        to obtain an estimate for the total energy.  Default value is 10000.
    equilenergysamples : int, optional
        The number of thermo samples from the end of the energy equilibrium
        stage to use in computing the target total energy.  Cannot be
        larger than equilenergysteps / 100.  Default value is 100.
    equilenergystyle : str, optional
        Indicates which scheme to use for computing the target total energy.
        Allowed values are 'pe' or 'te'.  For 'te', the average total energy
        from the equilenergysamples is used as the target energy.  For 'pe',
        the average potential energy plus 3/2 N kB T is used as the target
        energy.  Default value is 'pe'.
    runsteps : int or None, optional
        The number of nve integration steps to perform on the system to
        obtain measurements of MSD and RDF of the liquid. Default value is
        50000.
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps during the runsteps
        simulation. Default is None, which sets dumpsteps equal to the sum of
        all "steps" terms above so that only the final configuration is saved.
    restartsteps : int or None, optional
        Restart files will be saved every this many steps.  Default is None,
        which sets dumpsteps equal to the sum of all "steps" terms above so
        that only the final configuration is saved.
    createvelocities : bool, optional
        If True (default), velocities will be created for the atoms prior to
        running the simulations.  Setting this to False can be useful if the
        initial system already has velocity information.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_final'** (*str*) - The name of the final dump file
          created.
        - **'symbols_final'** (*list*) - The symbols associated with the final
          dump file.
        - **'volume'** (*float*) - The volume per atom identified after the volume 
          equilibration stage.
        - **'volume_stderr'** (*float*) - The standard error in the volume per atom
          measured during the volume equilibration stage.
        - **'E_total'** (*float*) - The total energy of the system used during the nve
          stage.
        - **'E_total_stderr'** (*float*) - The standard error in the mean total energy
          computed during the energy equilibration stage.
        - **'E_pot'** (*float*) - The mean measured potential energy during the energy
          equilibration stage.
        - **'E_pot_stderr'** (*float*) - The standard error in the mean potential energy
          during the energy equilibration stage.
        - **'measured_temp'** (*float*) - The mean measured temperature during the nve
          stage.
        - **'measured_temp_stderr'** (*float*) - The standard error in the measured
          temperature values of the nve stage.
        - **'measured_press'** (*float*) - The mean measured pressure during the nve
          stage.
        - **'measured_press_stderr'** (*float*) - The standard error in the measured
          pressure values of the nve stage.
        - **'time_values'** (*numpy.array of float*) - The values of time that
          correspond to the mean squared displacement values.
        - **'msd_x_values'** (*numpy.array of float*) - The mean squared displacement
          values only in the x direction.
        - **'msd_y_values'** (*numpy.array of float*) - The mean squared displacement
         values only in the y direction.
        - **'msd_z_values'** (*numpy.array of float*) - The mean squared displacement
         values only in the z direction.
        - **'msd_values'** (*numpy.array of float*) - The total mean squared
           displacement values.
        - **'lammps_output'** (*atomman.lammps.Log*) - The LAMMPS logfile output.
          Can be useful for checking the thermo data at each simulation stage.
    """
  
    if equilenergystyle not in ['pe', 'te']:
        raise ValueError('invalid equilenergystyle option: must be "pe" or "te"')

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Handle default values
    if dumpsteps is None:
        dumpsteps = meltsteps + coolsteps + equilvolumesteps + equilenergysteps + runsteps
    if restartsteps is None:
        restartsteps = meltsteps + coolsteps + equilvolumesteps + equilenergysteps + runsteps

    # Check volrelax and temprelax settings
    if equilvolumesamples > equilvolumesteps / 100:
        raise ValueError('invalid values: equilvolumesamples must be <= equilvolumesteps / 100')
    if equilenergysamples > equilenergysteps / 100:
        raise ValueError('invalid values: equilenergysamples must be <= equilenergysteps / 100')

    # Set default rdfcutoff
    if rdfcutoff is None:
        rdfcutoff = 4 * system.r0()

    # Define lammps variables
    lammps_variables = {}
    
    lammps_variables['boltzmann'] = uc.get_in_units(uc.unit['kB'],
                                                    lammps_units['energy'])
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Generate LAMMPS inputs for restarting
    system_info2 = potential.pair_restart_info('*.restart', system.symbols)
    lammps_variables['atomman_pair_restart_info'] = system_info2

    # Phase settings
    lammps_variables['temperature'] = temperature
    lammps_variables['temperature_melt'] = temperature_melt
    lammps_variables['pressure'] = pressure

    # Set timestep dependent parameters
    timestep = lmp.style.timestep(potential.units)
    lammps_variables['timestep'] = timestep
    lammps_variables['temperature_damp'] = 100 * timestep
    lammps_variables['pressure_damp'] = 1000 * timestep

    # Number of run/dump steps
    lammps_variables['meltsteps'] = meltsteps
    lammps_variables['coolsteps'] = coolsteps
    lammps_variables['equilvolumesteps'] = equilvolumesteps
    lammps_variables['equilenergysteps'] = equilenergysteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['restartsteps'] = restartsteps

    # Number of samples
    lammps_variables['equilvolumesamples'] = equilvolumesamples
    lammps_variables['equilenergysamples'] = equilenergysamples
    
    lammps_variables['rdfcutoff'] = rdfcutoff

    # Set randomseed
    if randomseed is None: 
        randomseed = random.randint(1, 900000000)

    # create velocities 
    if createvelocities:
        if meltsteps == 0 and coolsteps == 0:
            velocity_temp = temperature
        else:
            velocity_temp = temperature_melt
        lammps_variables['create_velocities'] = f'velocity all create {velocity_temp} {randomseed} mom yes rot yes dist gaussian'
    else:
        lammps_variables['create_velocities'] = ''

    # Set dump_keys based on atom_style
    if potential.atom_style in ['charge']:
        lammps_variables['dump_keys'] = 'id type q xu yu zu c_pe vx vy vz'
    else:
        lammps_variables['dump_keys'] = 'id type xu yu zu c_pe vx vy vz'

    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        if potential.atom_style in ['charge']:
            lammps_variables['dump_modify_format'] = f'"%d %d{8 * " %.13e"}"'
        else:
            lammps_variables['dump_modify_format'] = f'"%d %d{7 * " %.13e"}"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'

    # Write lammps input script
    lammps_script = 'liquid.in'
    lammps_template = f'liquid_ave_{equilenergystyle}.template'
    template = read_calc_file('iprPy.calculation.relax_liquid', lammps_template)
    with open(lammps_script, 'w', encoding='UTF-8') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Write lammps restart input script
    restart_script = 'liquid_restart.in'
    lammps_template = 'liquid_restart.template'
    template = read_calc_file('iprPy.calculation.relax_liquid', lammps_template)
    with open(restart_script, 'w', encoding='UTF-8') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Fix for restart runs: only use restart script if restart file(s) exist
    if Path('log.lammps').exists() and len(list(Path('.').glob('*.restart'))) == 0:
        Path('log.lammps').unlink()

    # Uniquely rename rdf.txt on restarts to prevent overwrite
    elif Path('rdf.txt').exists():
        maxrdfid = 0
        for oldrdf in Path('.').glob('rdf-*.txt'):
            rdfid = int(oldrdf.stem.split('-')[-1])
            if rdfid > maxrdfid:
                maxrdfid = rdfid
        Path('rdf.txt').rename(f'rdf-{maxrdfid+1}.txt')

    # Run lammps
    output = lmp.run(lammps_command, script_name=lammps_script,
                     restart_script_name=restart_script,
                     mpi_command=mpi_command, screen=False)

    # Extract LAMMPS thermo data.
    run1steps = meltsteps
    run2steps = run1steps + coolsteps
    run3steps = run2steps + equilvolumesteps
    run4steps = run3steps + equilenergysteps
    thermo = output.flatten()['thermo']
    #thermo_melt = thermo[thermo.Step < run1steps]
    #thermo_cool = thermo[(thermo.Step < run2steps) & (thermo.Step >= run1steps)]
    thermo_vol_equil = thermo[(thermo.Step < run3steps) & (thermo.Step >= run2steps)]
    thermo_temp_equil = thermo[(thermo.Step < run4steps) & (thermo.Step >= run3steps)]
    thermo_nve = thermo[thermo.Step >= run4steps]

    results = {}
    
    # Set final dumpfile info
    last_dump_number = 0
    for dump_file in Path('.').glob('*.dump'):
        dump_number = int(dump_file.name[:-5])
        if dump_number > last_dump_number:
            last_dump_number = dump_number
    last_dump_file = f'{last_dump_number}.dump'
    results['dumpfile_final'] = last_dump_file
    results['symbols_final'] = system.symbols
    
    natoms = system.natoms

    # Get equilibrated volume 
    volume_unit = f"{lammps_units['length']}^3"
    samplestart = len(thermo_vol_equil) - equilvolumesamples
    results['volume'] = uc.set_in_units(thermo_temp_equil.Volume.values[-1], volume_unit) / natoms
    results['volume_stderr'] = uc.set_in_units(thermo_vol_equil.Volume[samplestart:].std(), volume_unit) / natoms / (equilvolumesamples)**0.5

    # Get equilibrated energies
    samplestart = len(thermo_temp_equil) - equilenergysamples
    results['E_total'] = uc.set_in_units(thermo_nve.TotEng.values[-1], lammps_units['energy']) / natoms
    results['E_total_stderr'] = uc.set_in_units(thermo_temp_equil.TotEng[samplestart:].std(), lammps_units['energy']) / natoms / (equilenergysamples)**0.5
    results['E_pot'] = uc.set_in_units(thermo_temp_equil.PotEng[samplestart:].mean(), lammps_units['energy']) / natoms
    results['E_pot_stderr'] = uc.set_in_units(thermo_temp_equil.PotEng[samplestart:].std(), lammps_units['energy']) / natoms / (equilenergysamples)**0.5

    # Get measured temperature and pressure during the nve run
    nsamples = len(thermo_nve)
    results['measured_temp'] = thermo_nve.Temp.values.mean()
    results['measured_temp_stderr'] = thermo_nve.Temp.values.std() / (nsamples)**0.5
    pressure = (thermo_nve.Pxx.values + thermo_nve.Pyy.values + thermo_nve.Pzz.values) / 3
    results['measured_press'] = uc.set_in_units(pressure.mean(), lammps_units['pressure'])
    results['measured_press_stderr'] = uc.set_in_units(pressure.std(), lammps_units['pressure']) / (nsamples)**0.5
    
    # Get MSD values
    msd_unit = f"{lammps_units['length']}^2"
    time = (thermo_nve.Step.values - thermo_nve.Step.values[0]) * timestep
    results['time_values'] = uc.set_in_units(time, lammps_units['time'])
    results['msd_x_values'] = uc.set_in_units(thermo_nve['c_msd[1]'].values, msd_unit)
    results['msd_y_values'] = uc.set_in_units(thermo_nve['c_msd[2]'].values, msd_unit)
    results['msd_z_values'] = uc.set_in_units(thermo_nve['c_msd[3]'].values, msd_unit)
    results['msd_values'] = uc.set_in_units(thermo_nve['c_msd[4]'].values, msd_unit)

    results['lammps_output'] = output

    return results