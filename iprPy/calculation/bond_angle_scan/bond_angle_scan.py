# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from typing import Optional

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def bond_angle_scan(lammps_command: str,
                    potential: am.lammps.Potential, 
                    symbols: list,
                    mpi_command: Optional[str] = None,
                    rmin: float = uc.set_in_units(0.5, 'angstrom'), 
                    rmax: float = uc.set_in_units(6.0, 'angstrom'), 
                    rnum: int = 100,
                    thetamin: float = 1.0,
                    thetamax: float = 180,
                    thetanum: int = 100) -> dict:
    """
    Performs a three-body bond angle energy scan over a range of interatomic
    spaces, r, and angles, theta.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the three atoms in the cluster.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float, optional
        The minimum value for the r_ij and r_ik spacings. Default value is 0.5.
    rmax : float, optional
        The maximum value for the r_ij and r_ik spacings. Default value is 5.5.
    rnum : int, optional
        The number of r_ij and r_ik spacings to evaluate. Default value is 100.
    thetamin : float, optional
        The minimum value for the theta angle. Default value is 1.0.
    thetamax : float, optional
        The maximum value for the theta angle. Default value is 180.0.
    thetanum : int, optional
        The number of theta angles to evaluate. Default value is 100.
        
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'cluster'** (*atomman.cluster.BondAngleMap*) - Object that maps
          measured energies to r, theta coordinates, and contains built-in
          analysis tools.
        - **results_file'** (*str*) - File name containing the raw energy
          scan results.
        - **'length_unit'** (*str*) - Unit of length used in the results_file.
        - **'energy_unit'** (*str*) - Unit of energy used in the results_file.
    """
 
    # Create cluster object
    cluster = am.cluster.BondAngleMap(rmin=rmin, rmax=rmax, rnum=rnum,
                                      thetamin=thetamin, thetamax=thetamax,
                                      thetanum=thetanum, symbols=symbols)
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    
    # Add range parameters
    lammps_variables['rmin'] = uc.get_in_units(rmin, lammps_units['length'])
    lammps_variables['rmax'] = uc.get_in_units(rmax, lammps_units['length'])
    lammps_variables['rnum'] = uc.get_in_units(rnum, lammps_units['length'])
    lammps_variables['thetamin'] = thetamin
    lammps_variables['thetamax'] = thetamax
    lammps_variables['thetanum'] = thetanum

    # Add atomic types
    if len(cluster.symbols) == 1:
        natypes = 1
        atype = np.array([1,1,1])
        symbols = cluster.symbols
    elif len(cluster.symbols) == 3:
        symbols, atype = np.unique(cluster.symbols, return_inverse=True)
        atype += 1
        natypes = len(symbols) 
    lammps_variables['natypes'] = natypes
    lammps_variables['atype1'] = atype[0]
    lammps_variables['atype2'] = atype[1]
    lammps_variables['atype3'] = atype[2]
    
    # Add potential information
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['atom_style'] = potential.atom_style
    lammps_variables['units'] = potential.units

    # Build lammps input script
    lammps_script = 'bond_scan.in'
    template = read_calc_file('iprPy.calculation.bond_angle_scan', 'bond_scan.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps and extract data
    lmp.run(lammps_command, script_name=lammps_script, mpi_command=mpi_command, logfile=None, screen=False)
    cluster.load_table('3_body_scan.txt', length_unit=lammps_units['length'],
                       energy_unit=lammps_units['energy'])
    
    # Collect results
    results_dict = {}
    results_dict['cluster'] = cluster
    results_dict['results_file'] = '3_body_scan.txt'
    results_dict['length_unit'] = lammps_units['length']
    results_dict['energy_unit'] = lammps_units['energy']
    
    return results_dict