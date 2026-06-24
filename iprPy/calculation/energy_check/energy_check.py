# Python script created by Lucas Hale
# Suggested by Udo v. Toussaint

# Standard library imports
from typing import Optional, Union

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential
from atomman.lammps import LAMMPS, LAMMPSobj


def energy_check(lammps_command: Union[str, LAMMPSobj],
                 system: am.System,
                 potential: lammpspotential,
                 mpi_command: Optional[str] = None,
                 dumpforces: bool = False,
                 usefiles: bool = False) -> dict:
    """
    Performs a quick run 0 calculation to evaluate the potential energy of a
    configuration.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The atomic configuration to evaluate.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  Can only be given if
        lammps_command is a LAMMPS executable command.
    forces : bool, optional
        If True, the atomic forces will also be calculated and returned.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'PotEng'** (*float*) - The total potential energy of the system.
        - **'PotEngAtom'** (*float*) - The per-atom potential energy of the system.
        - **'Pxx'** (*float*) - The measured xx component of the pressure on the system.
        - **'Pyy'** (*float*) - The measured yy component of the pressure on the system.
        - **'Pzz'** (*float*) - The measured zz component of the pressure on the system.
        - **'Pxy'** (*float*) - The measured xy component of the pressure on the system.
        - **'Pxz'** (*float*) - The measured xz component of the pressure on the system.
        - **'Pyz'** (*float*) - The measured yz component of the pressure on the system.
        - **'F'** (*numpy.ndarray*) - The atomic forces, returned if forces is True.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Handle file generation settings
    if usefiles:
        logfile = 'log.lammps'
        script = 'run0.in'
    else:
        logfile = 'none'
        script = None

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    # Set up thermo style 
    lmp.cmd.thermo_style('custom', 'step', 'pe', 'pxx', 'pyy', 'pzz', 'pxy', 'pxz', 'pyz')
    lmp.cmd.thermo_modify('format', 'float', '%.17e')
    
    # Optionally dump forces to a file
    if usefiles or (not lmp.islib and dumpforces):
        lmp.cmd.dump('dumpy', 'all', 'custom', '1', 'forces.dump', 'id', 'type', ' fx', 'fy', 'fz')
        lmp.cmd.dump_modify('dumpy', 'format', 'float', '%.17e')
    
    # Perform a run 0 to evaluate the system
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

    # Add per-atom potential energy
    thermo['PotEngAtom'] = thermo['PotEng'] / system.natoms

    # Get forces directly or from the dump file
    if dumpforces:
        if lmp.islib:
            thermo['F'] = lmp.numpy.extract_atom('f', nelem=system.natoms, dim=3)
        else:
            system = am.load('atom_dump', 'forces.dump')
            thermo['F'] = system.atoms.force
        thermo['F'] = uc.set_in_units(thermo['F'], lmp.unitsdict['force'])
    
    return thermo