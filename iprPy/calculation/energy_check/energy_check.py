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
                 mpi_command: Optional[str] = None,
                 dumpforces: bool = False) -> dict:
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
    dumpforces : bool, optional
        If True, a dump file will also be created that contains evaluations of
        the atomic forces.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'E_pot_total'** (*float*) - The total potential energy of the system.
        - **'E_pot_atom'** (*float*) - The per-atom potential energy of the system.
        - **'P_xx'** (*float*) - The measured xx component of the pressure on the system.
        - **'P_yy'** (*float*) - The measured yy component of the pressure on the system.
        - **'P_zz'** (*float*) - The measured zz component of the pressure on the system.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info

    # Add dump lines if requested
    if dumpforces:
        lammps_variables['dump_lines'] = '\n'.join([
            'dump dumpy all custom 1 forces.dump id type x y z fx fy fz',
            'dump_modify dumpy format float %.13e', ''])
    else:
        lammps_variables['dump_lines'] = ''

    # Fill in lammps input script
    template = read_calc_file('iprPy.calculation.energy_check', 'run0.template')
    script = filltemplate(template, lammps_variables, '<', '>')
    
    # Run LAMMPS
    output = lmp.run(lammps_command, script=script,
                     mpi_command=mpi_command, logfile=None)
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    results = {}
    results['E_pot_total'] = uc.set_in_units(thermo.PotEng.values[-1],
                                             lammps_units['energy'])
    results['E_pot_atom'] = uc.set_in_units(thermo.v_peatom.values[-1],
                                            lammps_units['energy'])
    results['P_xx'] = uc.set_in_units(thermo.Pxx.values[-1],
                                      lammps_units['pressure'])
    results['P_yy'] = uc.set_in_units(thermo.Pyy.values[-1],
                                      lammps_units['pressure'])
    results['P_zz'] = uc.set_in_units(thermo.Pzz.values[-1],
                                      lammps_units['pressure'])
    return results
