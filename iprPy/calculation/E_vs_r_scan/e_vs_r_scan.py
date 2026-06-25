# Python script created by Lucas Hale

# Standard Python libraries
from copy import deepcopy
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def e_vs_r_scan(lammps_command: Union[str, LAMMPSobj],
                system: am.System,
                potential: lammpspotential,
                mpi_command: Optional[str] = None,
                ucell: Optional[am.System] = None, 
                rmin: unitfloat = '2.0 angstrom', 
                rmax: unitfloat = '6.0 angstrom',
                rsteps: int = 200,
                usefiles: bool = False) -> dict:
    """
    Performs a cohesive energy scan over a range of interatomic spaces, r.
    
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
    ucell : atomman.System, optional
        The fundamental unit cell corresponding to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    rmin : float or str, optional
        The minimum r spacing to use (default value is 2.0 angstroms).
    rmax : float or str, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 200).
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    rmin = uc.set_in_units(rmin)
    rmax = uc.set_in_units(rmax)

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
    natoms = system.natoms

    # Loop over values
    for i in range(rsteps):
        
        # Rescale system's box
        a = a_values[i]
        system.box_set(a = a * lx_a, 
                       b = a * ly_a, 
                       c = a * lz_a, 
                       alpha=alpha, beta=beta, gamma=gamma, scale=True)
        
        # Evaluate energy using a run0 calculation
        try:
            results = run0(lmp, system, logfile=f'run0-{i}-log.lammps', usefiles=usefiles)
        except:
            Ecoh_values[i] = np.nan
        else:
            Ecoh_values[i] = results['PotEng'] / natoms

    # Throw error if all runs failed.
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

def run0(lmp: LAMMPSobj,
         system: am.System,
         logfile: str = 'log.lammps',
         usefiles: bool = False) -> dict:
    """
    A simple run 0 evaluation of a system.

    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object, with potential information
        already set.
    system : atomman.System
        The system to perform the calculation on.
    logfile : str, optional
        Indicates where the LAMMPS log information is to be saved if
        usefiles=True.  Default value is 'log.lammps'
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    """

    # Handle file generation settings
    if usefiles:
        script = 'run0.in'
    else:
        logfile = 'none'
        script = None

    lmp.commands_string('\n# Pass system and potential info into LAMMPS')
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('\n# Set up thermo style')
    lmp.cmd.thermo_style('custom', 'step', 'pe')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    
    lmp.commands_string('\n# Perform a run 0 to evaluate the system')
    lmp.cmd.fix('nve', 'all', 'nve')
    lmp.cmd.run(0)

    # Run EXE versions, get log output
    log = lmp.end_and_get_log(script)

    if log is None:
        # Get thermo directly from lammps object if no log file
        thermo: dict = lmp.last_thermo()
    else:
        # Extract thermo terms from log output
        thermo = log.simulations[0].thermo.iloc[0].to_dict()

    # Convert units on standard thermo terms
    lmp.set_thermo_units(thermo)

    return thermo