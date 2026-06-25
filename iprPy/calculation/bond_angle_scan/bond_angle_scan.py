# Python script created by Lucas Hale

# Standard Python libraries
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj


def bond_angle_scan(lammps_command: Union[str, LAMMPSobj],
                    potential: lammpspotential, 
                    symbols: list,
                    mpi_command: Optional[str] = None,
                    rmin: unitfloat = '0.5 angstrom',
                    rmax: unitfloat = '6.0 angstrom',
                    rnum: int = 100,
                    thetamin: float = 1.0,
                    thetamax: float = 180,
                    thetanum: int = 100,
                    usefiles: bool = False) -> dict:
    """
    Performs a three-body bond angle energy scan over a range of interatomic
    spaces, r, and angles, theta.
    
    Parameters
    ----------
    lammps_command :str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    symbols : list
        The potential symbols associated with the three atoms in the cluster.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    rmin : float or str, optional
        The minimum value for the r_ij and r_ik spacings. Default value is
        0.5 angstrom.
    rmax : float or str, optional
        The maximum value for the r_ij and r_ik spacings. Default value is
        6.0 angstrom.
    rnum : int, optional
        The number of r_ij and r_ik spacings to evaluate. Default value is 100.
    thetamin : float, optional
        The minimum value for the theta angle. Default value is 1.0.
    thetamax : float, optional
        The maximum value for the theta angle in degrees. Default value is 180.0.
    thetanum : int, optional
        The number of theta angles to evaluate. Default value is 100.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.

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
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Handle file generation settings
    if usefiles or not lmp.islib:
        logfile = 'log.lammps'
        script = 'bond_scan.in'
    else:
        logfile = None
        script = None

    # Convert values given with units if needed
    rmin = uc.set_in_units(rmin)
    rmax = uc.set_in_units(rmax)

    # Create cluster object
    cluster = am.cluster.BondAngleMap(rmin=rmin, rmax=rmax, rnum=rnum,
                                      thetamin=thetamin, thetamax=thetamax,
                                      thetanum=thetanum, symbols=symbols)

    # Identify atomic types for the cluster
    if len(cluster.symbols) == 1:
        natypes = 1
        atype = np.array([1,1,1])
        symbols = cluster.symbols
    elif len(cluster.symbols) == 3:
        symbols, atype = np.unique(cluster.symbols, return_inverse=True)
        atype += 1
        natypes = len(symbols)

    ####### LAMMPS simulation #######

    lmp.commands_string('\n# Specify loop ranges')
    lmp.cmd.variable("rmin", "equal", uc.get_in_units(rmin, lmp.unitsdict['length']))
    lmp.cmd.variable("rmax", "equal", uc.get_in_units(rmax, lmp.unitsdict['length']))
    lmp.cmd.variable("rnum", "equal", rnum)
    lmp.cmd.variable("thetamin", "equal", thetamin)
    lmp.cmd.variable("thetamax", "equal", thetamax)
    lmp.cmd.variable("thetanum", "equal", thetanum)

    lmp.commands_string('\n# Define variable atom coordinates')
    lmp.cmd.variable("rij", "equal", "${rmin}+(v_i-1)*(${rmax}-${rmin})/(${rnum}-1)")
    lmp.cmd.variable("rik", "equal", "${rmin}+(v_j-1)*(${rmax}-${rmin})/(${rnum}-1)")
    lmp.cmd.variable("theta", "equal", "${thetamin}+(v_k-1)*(${thetamax}-${thetamin})/(${thetanum}-1)")
    lmp.cmd.variable("rtheta", "equal", "v_theta*PI/180.0")
    lmp.cmd.variable("j_x", "equal", "v_rij")
    lmp.cmd.variable("k_x", "equal", "v_rik*cos(v_rtheta)")
    lmp.cmd.variable("k_y", "equal", "v_rik*sin(v_rtheta)")
    lmp.cmd.variable("energy", "equal", "pe")

    lmp.commands_string('\n# Define box bounds based on rmax')
    lmp.cmd.variable("rlo", "equal", "-3*${rmax}")
    lmp.cmd.variable("rhi", "equal", "3*${rmax}")

    lmp.commands_string('\n# Initialize system')
    box = am.Box(xlo=-3*rmax, xhi=3*rmax, ylo=-3*rmax, yhi=3*rmax, zlo=-3*rmax, zhi=3*rmax)
    system = am.System(box=box, pbc=(False, False, False), symbols=symbols)
    lmp.new_system_no_atoms(system, potential, logfile=logfile)

    lmp.commands_string('\n# Define thermo style')
    lmp.cmd.thermo_style("custom", "step", "pe")
    lmp.cmd.thermo_modify("format", "float", "%.13e")

    # Create the atoms. Will shift atoms 2 and 3 later
    lmp.commands_string('\n# Create atoms')
    lmp.cmd.create_atoms(atype[0], 'single', 0.0, 0.0, 0.0, 'units', 'box')
    lmp.cmd.create_atoms(atype[1], 'single', 0.0, 0.0, 0.0, 'units', 'box')
    lmp.cmd.create_atoms(atype[2], 'single', 0.0, 0.0, 0.0, 'units', 'box')

    # Define integrator to keep LAMMPS from complaining
    lmp.cmd.fix('nve', 'all', 'nve')

    # Add charges if required
    if potential.atom_style == 'charge':
        charges = potential.charges(symbols)
        lmp.cmd.set('atom', 1, 'charge', charges[atype[0]-1])
        lmp.cmd.set('atom', 2, 'charge', charges[atype[1]-1])
        lmp.cmd.set('atom', 3, 'charge', charges[atype[2]-1])

    lmp.commands_string('\n# Start 3_body_scan.txt with header fields')
    lmp.cmd.print('"${rmin} ${rmax} ${rnum}"', "file", "3_body_scan.txt", "screen", "no")
    lmp.cmd.print('"${rmin} ${rmax} ${rnum}"', "append", "3_body_scan.txt", "screen", "no")
    lmp.cmd.print('"${thetamin} ${thetamax} ${thetanum}"', "append", "3_body_scan.txt", "screen", "no")

    lmp.commands_string('\n# Loop i over r_ij values')
    for i in lmp.loop('i', rnum, usefiles=usefiles):
    
        lmp.commands_string("\n# Update atom 2's x coordinate")
        lmp.cmd.set('atom', 2, 'x', '${j_x}')

        lmp.commands_string('\n# Loop j over r_ik values')
        for j in lmp.loop('j', rnum, usefiles=usefiles):
        
            lmp.commands_string('\n# Loop k over theta values')
            for k in lmp.loop('k', thetanum, usefiles=usefiles):

                lmp.commands_string("\n# Update atom 3's x and y coordinates and evaluate")
                lmp.cmd.set('atom', 3, 'x', '${k_x}', 'y', '${k_y}')
                lmp.cmd.run(0)
                lmp.cmd.print('"${i} ${j} ${k} ${energy}"', 'append', '3_body_scan.txt', 'screen', 'no')

    # Run EXE versions, get log output
    lmp.end_and_get_log(script, return_log=False)
    
    cluster.load_table('3_body_scan.txt', length_unit=lmp.unitsdict['length'],
                       energy_unit=lmp.unitsdict['energy'])
    
    # Collect results
    results_dict = {}
    results_dict['cluster'] = cluster
    results_dict['results_file'] = '3_body_scan.txt'
    results_dict['length_unit'] = lmp.unitsdict['length']
    results_dict['energy_unit'] = lmp.unitsdict['energy']
    
    return results_dict
