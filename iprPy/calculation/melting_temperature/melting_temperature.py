# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union
from pathlib import Path
import random

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

import numpy as np

# iprPy imports
from ...tools import read_calc_file

def melting_temperature(lammps_command: str,
                        system: am.System,
                        potential: lmp.Potential,
                        temperature_guess: float,
                        mpi_command: Optional[str] = None,
                        pressure: float = 0.0,
                        temperature_solid: Optional[float] = None,
                        temperature_liquid: Optional[float] = None,
                        ptm_structures: Optional[str] = None,
                        meltsteps: int = 10000,
                        scalesteps: int = 10000,
                        runsteps: int = 200000,
                        thermosteps: int = 100,
                        dumpsteps: Optional[int] = None,
                        randomseed: Union[int, list] = None) -> dict:
    """
    Creates a solid-liquid phase coexistence simulation to estimate the melting
    temperature.  The boundary for the two phases will be perpendicular to the
    z-axis and positioned halfway along the c box vector.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The initial system to perform the calculation on.  This should be a
        supercell with dimensions along the z direction roughly twice the
        dimensions in the other directions.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature_guess : float, optional
        The initial guess for the melting temperature. The closer to the actual
        temperature the faster and more likely convergence will be possible.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    pressure : float, optional
        The target pressure to use with the barostat.  Default value is 0.0.
    temperature_liquid : float or None, optional
        The initial temperature to use for the liquid region to melt the crystal.
        Default value of None will use 1.25 * temperature_guess.
    temperature_solid : float or None, optional
        The initial temperature to use for the solid region.
        Default value of None will use 0.5 * temperature_guess.
    meltsteps : int, optional
        The number of integration steps to perform with half of the system
        at temperature_solid and half of the system at temperature_liquid to
        create the two phase configuration.  Default value is 10000.
    scalesteps : int, optional
        The number of integration steps after meltsteps where the temperature
        of the atoms in the two phases are both scaled to temperature_guess.
        This ensures that the full system starts near temperature_guess for the
        main runsteps.  Default value is 10000.
    runsteps : int, optional
        The number of nph integration steps to perform on the two-phase system
        to hopefully get a stable coexistence at the melting temperature.
    thermosteps : int, optional
        Thermo values will be reported every this many steps. Default is
        100.
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps. Default is None,
        which sets dumpsteps equal to meltsteps + scalesteps + runsteps.
    randomseed : int, list or None, optional
        Random number seed(s) used by LAMMPS in creating velocities for the liquid
        and solid regions.  Default is None which will select random ints
        between 1 and 900000000.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'temp'** (*float*) - The mean measured temperature.
    """
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Handle default values
    if dumpsteps is None:
        dumpsteps = meltsteps + scalesteps + runsteps
    if temperature_liquid is None:
        temperature_liquid = 1.25 * temperature_guess
    if temperature_solid is None:
        temperature_solid = 0.5 * temperature_guess
    
    # Random seed settings
    if randomseed is None:
        randomseed = random.randint(1, 900000000)
        
    # Define lammps variables
    lammps_variables = {}
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    lammps_variables['zboundary'] = system.box.origin[2] + 0.5 * system.box.cvect[2] 
    lammps_variables['temperature_guess'] = temperature_guess
    lammps_variables['temperature_liquid'] = temperature_liquid
    lammps_variables['temperature_solid'] = temperature_solid
    lammps_variables['pressure'] = pressure
    lammps_variables['meltsteps'] = meltsteps
    lammps_variables['scalesteps'] = scalesteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['randomseed'] = randomseed
    
    if ptm_structures is None:
        lammps_variables['compute_ptm'] = ''
        lammps_variables['ptm_dump'] = ''
    else:
        lammps_variables['compute_ptm'] = f'compute ptm all ptm/atom {ptm_structures} 0.15'
        lammps_variables['ptm_dump'] = 'c_ptm[1]'

    timestep = lmp.style.timestep(potential.units)
    lammps_variables['timestep'] = timestep
    
    # Write lammps input script
    lammps_script = 'two_phase_melting_temp.in'
    template = read_calc_file('iprPy.calculation.melting_temperature',
                              'two_phase_melting_temp.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
    
    thermo = output.simulations[2].thermo
    
    results_dict = {}
    results_dict['melting_temperature'] = thermo.Temp[round(len(thermo)/2):].mean()

    results_dict['fraction_solids'] = []
    if ptm_structures is not None:
        first_to_read = meltsteps + scalesteps + runsteps / 2
        for i in range(dumpsteps, meltsteps + scalesteps + runsteps+1, dumpsteps):
            if i < first_to_read:
                continue
            dump = am.load('atom_dump', f'{i}.dump')
            num_solid = np.sum(dump.atoms.view['c_ptm[1]'] != 0)
            results_dict['fraction_solids'].append(num_solid / dump.natoms)

    return results_dict