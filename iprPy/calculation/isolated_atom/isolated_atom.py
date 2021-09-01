# coding: utf-8

# Python script created by Lucas Hale

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# iprPy imports
from ...tools import filltemplate, read_calc_file

# Define calculation metadata
parent_module = '.'.join(__name__.split('.')[:-1])

def isolated_atom(lammps_command, potential, mpi_command=None):
    """
    Evaluates the isolated atom energy for each elemental model of a potential.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'energy'** (*dict*) - The computed potential energies for each
          symbol.
    """
    # Initialize dictionary
    energydict = {}
    
    # Initialize single atom system 
    box = am.Box.cubic(a=1)
    atoms = am.Atoms(atype=1, pos=[[0.5, 0.5, 0.5]])
    system = am.System(atoms=atoms, box=box, pbc=[False, False, False])

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    # Define lammps variables
    lammps_variables = {}

    # Loop over symbols
    for symbol in potential.symbols:
        system.symbols = symbol

        # Add charges if required
        if potential.atom_style == 'charge':
            system.atoms.prop_atype('charge', potential.charges(system.symbols))

        # Save configuration
        system_info = system.dump('atom_data', f='isolated.dat',
                                  potential=potential)
        lammps_variables['atomman_system_pair_info'] = system_info
        
        # Write lammps input script
        template_file = 'run0.template'
        lammps_script = 'run0.in'
        template = read_calc_file(parent_module, template_file)
        with open(lammps_script, 'w') as f:
            f.write(filltemplate(template, lammps_variables, '<', '>'))
        
        # Run lammps and extract data
        output = lmp.run(lammps_command, script_name=lammps_script,
                         mpi_command=mpi_command)
        energy = output.simulations[0]['thermo'].PotEng.values[-1]
        energydict[symbol] = uc.set_in_units(energy, lammps_units['energy'])
    
    # Collect results
    results_dict = {}
    results_dict['energy'] = energydict
    
    return results_dict