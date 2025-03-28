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

from DataModelDict import DataModelDict as DM

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
                 meltsteps: int = 50000,
                 coolsteps: int = 10000,
                 equilvolumesteps: int = 50000,
                 equilvolumesamples: int = 300,
                 runsteps: int = 20000,
                 dumpsteps: int = 100,
                 restartsteps: Optional[int] = None,
                 createvelocities: bool = True,
                 rdf_nbins = 400,
                 rdf_minr = 0.0,
                 rdf_maxr = 10.0,
                 rdf_delete_dump = True,
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
    runsteps : int or None, optional
        The number of nvt integration steps to perform on the system at the
        averaged volume to measure the RDF of the liquid. Default value is
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
        - **'lx'** (*float*) - The mean lx box length measured during the volume
          equilibration stage.
        - **'lx_stderr'** (*float*) - The standard error in the lx box length
          measured during the volume equilibration stage.
        - **'ly'** (*float*) - The mean ly box length measured during the volume
          equilibration stage.
        - **'ly_stderr'** (*float*) - The standard error in the ly box length
          measured during the volume equilibration stage.
        - **'lz'** (*float*) - The mean lz box length measured during the volume
          equilibration stage.
        - **'lz_stderr'** (*float*) - The standard error in the lz box length
          measured during the volume equilibration stage.
        - **'E_total'** (*float*) - The mean total energy per atom computed during the
          nvt stage.
        - **'E_total_stderr'** (*float*) - The standard error in the mean total energy
          computed during the nvt stage.
        - **'E_pot'** (*float*) - The mean potential energy per atom computed during
          the nvt stage.
        - **'E_pot_stderr'** (*float*) - The standard error in the mean potential energy
          during the nvt stage.
        - **'measured_temp'** (*float*) - The mean measured temperature during the nvt
          stage.
        - **'measured_temp_stderr'** (*float*) - The standard error in the measured
          temperature values of the nvt stage.
        - **'measured_press'** (*float*) - The mean measured pressure during the nvt
          stage.
        - **'measured_press_stderr'** (*float*) - The standard error in the measured
          pressure values of the nvt stage.
    """
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Handle default values
    if dumpsteps is None:
        dumpsteps = meltsteps + coolsteps + equilvolumesteps + runsteps
    if restartsteps is None:
        restartsteps = meltsteps + coolsteps + equilvolumesteps + runsteps

    # Check volrelax settings
    if equilvolumesamples > equilvolumesteps / 100:
        raise ValueError('invalid values: equilvolumesamples must be <= equilvolumesteps / 100')

    # Define lammps variables
    lammps_variables = {}

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
    lammps_variables['pressure'] = uc.get_in_units(pressure, lammps_units['pressure'])

    # Set timestep dependent parameters
    timestep = lmp.style.timestep(potential.units)
    lammps_variables['timestep'] = timestep
    lammps_variables['temperature_damp'] = 100 * timestep
    lammps_variables['pressure_damp'] = 1000 * timestep

    # Number of run/dump steps
    lammps_variables['meltsteps'] = meltsteps
    lammps_variables['coolsteps'] = coolsteps
    lammps_variables['equilvolumesteps'] = equilvolumesteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['restartsteps'] = restartsteps

    # Number of samples
    lammps_variables['equilvolumesamples'] = equilvolumesamples

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
    lammps_template = 'liquid.template'
    template = read_calc_file('iprPy.calculation.relax_liquid_redo', lammps_template)
    with open(lammps_script, 'w', encoding='UTF-8') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Write lammps restart input script
    restart_script = 'liquid_restart.in'
    lammps_template = 'liquid_restart.template'
    template = read_calc_file('iprPy.calculation.relax_liquid_redo', lammps_template)
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

    # Extract LAMMPS thermo data
    run1steps = meltsteps
    run2steps = run1steps + coolsteps
    run3steps = run2steps + equilvolumesteps
    thermo = output.flatten()['thermo']
    thermo_melt = thermo[thermo.Step < run1steps]
    thermo_cool = thermo[(thermo.Step < run2steps) & (thermo.Step >= run1steps)]
    thermo_vol_equil = thermo[(thermo.Step < run3steps) & (thermo.Step >= run2steps)]
    thermo_nvt = thermo[thermo.Step >= run3steps]

    # Simple way doesn't work with restarts...
    #thermo_melt = output.simulations[0].thermo
    #thermo_cool = output.simulations[1].thermo
    #thermo_vol_equil = output.simulations[2].thermo
    #thermo_nvt = output.simulations[3].thermo

    # Compute RDF from dump files
    compute_ave_rdf(rdf_nbins, rdf_minr, rdf_maxr)

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

    if rdf_delete_dump:
        for dump_file in Path('.').glob('*.dump'):
            if dump_file.name != last_dump_file:
                dump_file.unlink()

    natoms = system.natoms

    relaxed_system = am.load('atom_dump', last_dump_file)
    volume = relaxed_system.box.volume
    lx = relaxed_system.box.lx
    ly = relaxed_system.box.ly
    lz = relaxed_system.box.lz

    # Get final box dimensions, and stderr of said values from vol_equil run
    volume_unit = f"{lammps_units['length']}^3"
    samplestart = len(thermo_vol_equil) - equilvolumesamples
    results['volume'] = uc.set_in_units(volume, volume_unit) / natoms
    results['volume_stderr'] = uc.set_in_units(thermo_vol_equil.Volume[samplestart:].std(), volume_unit) / natoms / (equilvolumesamples)**0.5
    results['lx'] = uc.set_in_units(lx, lammps_units['length'])
    results['lx_stderr'] = uc.set_in_units(thermo_vol_equil.Lx[samplestart:].std(), lammps_units['length']) / (equilvolumesamples)**0.5
    results['ly'] = uc.set_in_units(ly, lammps_units['length'])
    results['ly_stderr'] = uc.set_in_units(thermo_vol_equil.Ly[samplestart:].std(), lammps_units['length']) / (equilvolumesamples)**0.5
    results['lz'] = uc.set_in_units(lz, lammps_units['length'])
    results['lz_stderr'] = uc.set_in_units(thermo_vol_equil.Lz[samplestart:].std(), lammps_units['length']) / (equilvolumesamples)**0.5

    # Get measured values during the nvt run
    nsamples = len(thermo_nvt)
    results['E_total'] = uc.set_in_units(thermo_nvt.TotEng.mean(), lammps_units['energy']) / natoms
    results['E_total_stderr'] = uc.set_in_units(thermo_nvt.TotEng.std(), lammps_units['energy']) / natoms / (nsamples)**0.5
    results['E_pot'] = uc.set_in_units(thermo_nvt.PotEng.mean(), lammps_units['energy']) / natoms
    results['E_pot_stderr'] = uc.set_in_units(thermo_nvt.PotEng.std(), lammps_units['energy']) / natoms / (nsamples)**0.5
    results['measured_temp'] = thermo_nvt.Temp.values.mean()
    results['measured_temp_stderr'] = thermo_nvt.Temp.values.std() / (nsamples)**0.5
    pressure = (thermo_nvt.Pxx.values + thermo_nvt.Pyy.values + thermo_nvt.Pzz.values) / 3
    results['measured_press'] = uc.set_in_units(pressure.mean(), lammps_units['pressure'])
    results['measured_press_stderr'] = uc.set_in_units(pressure.std(), lammps_units['pressure']) / (nsamples)**0.5

    return results

def compute_ave_rdf(nbins=200, rmin=0.0, rmax=10.0):
    
    gs = []
    coords = []
    for dumpfile in Path('.').glob('*.dump'):
        system = am.load('atom_dump', dumpfile)
        r, g, coord = compute_rdf(system, nbins, rmin, rmax)
        gs.append(g)
        coords.append(coord)

    g = np.mean(gs, axis=0)
    coord = np.mean(coords, axis=0)

    with open('rdf_dump.txt', 'w') as f:
        f.write('# RDF data computed from dump files\n')
        f.write('# Unused Number-of-rows\n')
        f.write('# Row r rdf coord\n')
        f.write(f'0 {r.shape[0]}\n')
        for i in range(r.shape[0]):
            f.write(f'{i+1} {r[i]} {g[i]} {coord[i]}\n')

def compute_rdf(system, nbins, rmin, rmax):
    """Compute the RDF from a system"""

    system.wrap()
    natoms = system.natoms
    volume = system.box.volume

    sizemults = [1, 1, 1]
    if system.box.lx <= 2 * rmax:
        sizemults[0] = (-1, 2)
    if system.box.ly <= 2 * rmax:
        sizemults[1] = (-1, 2)
    if system.box.lz <= 2 * rmax:
        sizemults[2] = (-1, 2)
    bigsystem = system.supersize(*sizemults)

    # Create empty histogram and find the edges
    counts, edges = np.histogram(np.array([]), nbins, range=(rmin, rmax), density=False)
    mid_r = (edges[1:] + edges[:-1]) / 2
    delta_r = edges[1] - edges[0]

    # Compute the denominator
    denom = (4 * np.pi * natoms * (natoms - 1) / volume * mid_r**2) * delta_r

    # Loop over all atoms
    j_ids = np.arange(bigsystem.natoms)
    for i_id in range(natoms):

        # Find shortest distance to every other atom
        dmags = bigsystem.dmag(system.atoms.pos[i_id], j_ids)

        # Add to the histogram
        counts += np.histogram(dmags, nbins, range=(rmin, rmax), density=False)[0]

    # Remove 0 count
    if rmin == 0:
        counts[0] = 0
    
    # Compute coord and g
    coord = np.cumsum(counts) / natoms
    g = counts / denom

    return mid_r, g, coord