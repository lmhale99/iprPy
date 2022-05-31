# coding: utf-8

# Python script created by Lucas Hale
# Suggested by Udo v. Toussaint

# Standard library imports
from typing import Optional

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def energy_check(lammps_command: str,
                 system: am.System,
                 potential: lmp.Potential,
                 mpi_command: Optional[str] = None) -> dict:
    """
    Performs a quick run 0 calculation to evaluate the potential energy of a
    configuration.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The atomic configuration to evaluate.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'E_pot'** (*float*) - The per-atom potential energy of the system.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Fill in lammps input script
    template = read_calc_file('iprPy.calculation.energy_check', 'run0.template')
    script = filltemplate(template, lammps_variables, '<', '>')
    
    # Run LAMMPS
    output = lmp.run(lammps_command, script=script,
                     mpi_command=mpi_command, logfile=None)
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    results = {}
    results['E_pot'] = uc.set_in_units(thermo.v_peatom.values[-1],
                                       lammps_units['energy'])
    
    return results
    