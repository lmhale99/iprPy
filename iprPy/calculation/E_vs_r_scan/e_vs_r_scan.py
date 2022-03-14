# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from copy import deepcopy
import datetime
import shutil
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def e_vs_r_scan(lammps_command: str,
                system: am.System,
                potential: am.lammps.Potential,
                mpi_command: Optional[str] = None,
                ucell: Optional[am.System] = None, 
                rmin: float = uc.set_in_units(2.0, 'angstrom'), 
                rmax: float = uc.set_in_units(6.0, 'angstrom'),
                rsteps: int = 200) -> dict:
    """
    Performs a cohesive energy scan over a range of interatomic spaces, r.
    
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
    ucell : atomman.System, optional
        The fundamental unit cell correspodning to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    rmin : float, optional
        The minimum r spacing to use (default value is 2.0 angstroms).
    rmax : float, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 200).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'a_values'** (*numpy.array of float*) - All unit cell a lattice
          constants corresponding to the values explored.
        - **'Ecoh_values'** (*numpy.array of float*) - The computed cohesive
          energies for each r value.
        - **'min_cell'** (*list of atomman.System*) - Systems corresponding to
          the minima identified in the Ecoh_values.
    """

    # Make system a deepcopy of itself (protect original from changes)
    system = deepcopy(system)
    
    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Calculate the r/a ratio for the unit cell
    r_a = ucell.r0() / ucell.box.a
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_a = system.box.b / ucell.box.a
    lz_a = system.box.c / ucell.box.a
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
 
    # Build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    a_values = r_values / r_a
    Ecoh_values = np.empty(rsteps)
    
    # Loop over values
    for i in range(rsteps):
        
        # Rescale system's box
        a = a_values[i]
        system.box_set(a = a * lx_a, 
                       b = a * ly_a, 
                       c = a * lz_a, 
                       alpha=alpha, beta=beta, gamma=gamma, scale=True)
        
        # Get lammps units
        lammps_units = lmp.style.unit(potential.units)
        
        # Define lammps variables
        lammps_variables = {}
        system_info = system.dump('atom_data', f='atom.dat',
                                  potential=potential)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        # Write lammps input script
        lammps_script = 'run0.in'
        template = read_calc_file('iprPy.calculation.E_vs_r_scan', 'run0.template')
        with open(lammps_script, 'w') as f:
            f.write(filltemplate(template, lammps_variables, '<', '>'))
        
        # Run lammps and extract data
        try:
            output = lmp.run(lammps_command, script_name=lammps_script,
                             mpi_command=mpi_command)
        except:
            Ecoh_values[i] = np.nan
        else:
            thermo = output.simulations[0]['thermo']
            
            if output.lammps_date < datetime.date(2016, 8, 1):
                Ecoh_values[i] = uc.set_in_units(thermo.peatom.values[-1],
                                                lammps_units['energy'])
            else:
                Ecoh_values[i] = uc.set_in_units(thermo.v_peatom.values[-1],
                                                lammps_units['energy'])
        
        # Rename log.lammps
        try:
            shutil.move('log.lammps', 'run0-'+str(i)+'-log.lammps')
        except:
            pass

    if len(Ecoh_values[np.isfinite(Ecoh_values)]) == 0:
        raise ValueError('All LAMMPS runs failed. Potential likely invalid or incompatible.')  
    
    # Find unit cell systems at the energy minimums
    min_cells = []
    for i in range(1, rsteps - 1):
        if (Ecoh_values[i] < Ecoh_values[i-1]
            and Ecoh_values[i] < Ecoh_values[i+1]):
            a = a_values[i]
            cell = deepcopy(ucell)
            cell.box_set(a = a,
                         b = a * ucell.box.b / ucell.box.a,
                         c = a * ucell.box.c / ucell.box.a, 
                         alpha=alpha, beta=beta, gamma=gamma, scale=True)
            min_cells.append(cell)
    
    # Collect results
    results_dict = {}
    results_dict['r_values'] = r_values
    results_dict['a_values'] = a_values
    results_dict['Ecoh_values'] = Ecoh_values
    results_dict['min_cell'] = min_cells
    
    return results_dict
