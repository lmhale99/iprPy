# coding: utf-8

# Python script created by Lucas Hale

# http://www.numpy.org/
import numpy as np


# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from ...tools import filltemplate, read_calc_file, aslist

# Define calculation metadata
parent_module = '.'.join(__name__.split('.')[:-1])

def diatom_scan(lammps_command, potential, symbols,
                mpi_command=None, 
                rmin=uc.set_in_units(0.02, 'angstrom'), 
                rmax=uc.set_in_units(6.0, 'angstrom'), rsteps=300):
    """
    Performs a diatom energy scan over a range of interatomic spaces, r.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the two atoms in the diatom.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float, optional
        The minimum r spacing to use (default value is 0.02 angstroms).
    rmax : float, optional
        The maximum r spacing to use (default value is 6.0 angstroms).
    rsteps : int, optional
        The number of r spacing steps to evaluate (default value is 300).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'r_values'** (*numpy.array of float*) - All interatomic spacings,
          r, explored.
        - **'energy_values'** (*numpy.array of float*) - The computed potential
          energies for each r value.
    """
 
    # Build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    energy_values = np.empty(rsteps)
    
    # Define atype based on symbols
    symbols = aslist(symbols)
    if len(symbols) == 1:
        atype = [1, 1]
    elif len(symbols) == 2:
        atype = [1, 2]
    else:
        raise ValueError('symbols must have one or two values')
    
    # Initialize system (will shift second atom's position later...)
    box = am.Box.cubic(a = rmax + 1)
    atoms = am.Atoms(atype=atype, pos=[[0.1, 0.1, 0.1], [0.1, 0.1, 0.1]])
    system = am.System(atoms=atoms, box=box, pbc=[False, False, False], symbols=symbols)

    # Add charges if required
    if potential.atom_style == 'charge':
        system.atoms.prop_atype('charge', potential.charges(system.symbols))

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Define lammps variables
    lammps_variables = {}

    # Loop over values
    for i in range(rsteps):
        
        # Shift second atom's x position
        system.atoms.pos[1] = np.array([0.1 + r_values[i], 0.1, 0.1])

        # Save configuration
        system_info = system.dump('atom_data', f='diatom.dat',
                                  potential=potential)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        # Write lammps input script
        template_file = 'run0.template'
        lammps_script = 'run0.in'
        template = read_calc_file(parent_module, template_file)
        with open(lammps_script, 'w') as f:
            f.write(filltemplate(template, lammps_variables, '<', '>'))
        
        # Run lammps and extract data
        try:
            output = lmp.run(lammps_command, script_name=lammps_script,
                             mpi_command=mpi_command)
        except:
            energy_values[i] = np.nan
        else:
            energy = output.simulations[0]['thermo'].PotEng.values[-1]
            energy_values[i] = uc.set_in_units(energy, lammps_units['energy'])

    if len(energy_values[np.isfinite(energy_values)]) == 0:
        raise ValueError('All LAMMPS runs failed. Potential likely invalid or incompatible.')
    
    # Collect results
    results_dict = {}
    results_dict['r_values'] = r_values
    results_dict['energy_values'] = energy_values
    
    return results_dict

