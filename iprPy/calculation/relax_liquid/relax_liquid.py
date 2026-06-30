# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj
from atomman.thermo import RDF

def relax_liquid(lammps_command: Union[str, LAMMPSobj],
                 system: am.System,
                 potential: lammpspotential,
                 temperature: float,
                 mpi_command: Optional[str] = None,
                 pressure: unitfloat = 0.0,
                 temperature_melt: float = 3000.0,
                 meltsteps: int = 50000,
                 equilsteps: int = 20000,
                 runsteps: int = 1000000,
                 dumpsteps: Optional[int] = None,
                 restartsteps: Optional[int] = None,
                 createvelocities: bool = True,
                 rdf_nbins: int = 400,
                 rdf_minr: unitfloat = 0.0,
                 rdf_maxr: unitfloat = '10.0 angstrom',
                 rdf_delete_dump = True,
                 randomseed: Optional[int] = None,
                 usefiles: bool = False) -> dict:
    """
    Performs an npt simulation with coupled box dimensions to obtain a liquid
    phase configuration at a given temperature. Can be used for creating an
    initial melt phase or for continuing relaxation of a previous melt phase.
    
    Radial displacement functions are automatically computed for the system
    based on generated dump files allowing for any arbitrary cutoff distance.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    temperature : float
        The target temperature to relax to.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    pressure : float or str, optional
        The target hydrostatic pressure to relax to. Default value is 0 GPa.
    temperature_melt : float, optional
        The elevated temperature to first use to hopefully melt the initial
        configuration during the meltsteps.
    meltsteps : int, optional
        The number of npt integration steps to perform at the melt temperature
        to create an amorphous liquid structure.  Default value is 50,000.
    equilsteps : int, optional
        The number of npt integration steps to perform at the target temperature
        and pressure prior to collecting the thermo and dump files for property
        evaluation.  Default value is 20,000.
    runsteps : int or None, optional
        The number of npt integration steps to perform at the target temperature
        and pressure where thermo and dump files are used for property
        evaluation.  Default value is 1,000,000.
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps during the runsteps
        simulation.  Note that these are used to compute the RDF curve rather
        than using the LAMMPS method to allow for larger RDF cutoffs.  Default
        value of None will use runsteps / 100.
    restartsteps : int or None, optional
        Restart files will be saved every this many steps.  Default is None,
        which will not create restart files.
    createvelocities : bool, optional
        If True (default), velocities will be created for the atoms prior to
        running the simulations.  Setting this to False can be useful if the
        initial system already has velocity information.
    rdf_nbins : int, optional
        The number of bins to use for the RDF calculation.  Default value is
        400.
    rdf_minr : float or str, optional
        The minimum radial distance for the RDF calculation.  Default value
        is 0.0 angstroms.
    rdf_maxr: float or str, optional
        The mxaimum radial distance for the RDF calculation.  Default value
        is 10.0 angstroms.
    rdf_delete_dump : bool, optional
        If True (default), all dump files except for the final one will be
        deleted after the RDF calculation.  Setting this to False will leave
        all dump files allowing for further analysis.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_final'** (*str*) - The name of the final dump file
          created.
        - **'symbols_final'** (*list*) - The symbols associated with the final
          dump file.
        - **'E_pot'** (*float*) - The mean measured potential energy during the energy
          equilibration stage.
        - **'E_pot_stderr'** (*float*) - The standard error in the mean potential energy
          during the energy equilibration stage.
        - **'E_total'** (*float*) - The total energy of the system used during the nve
          stage.
        - **'E_total_stderr'** (*float*) - The standard error in the mean total energy
          computed during the energy equilibration stage.
        - **'volume'** (*float*) - The volume per atom identified after the volume 
          equilibration stage.
        - **'volume_stderr'** (*float*) - The standard error in the volume per atom
          measured during the volume equilibration stage.
        - **'measured_press'** (*float*) - The mean measured pressure during the nve
          stage.
        - **'measured_press_stderr'** (*float*) - The standard error in the measured
          pressure values of the nve stage.
        - **'measured_temp'** (*float*) - The mean measured temperature during the nve
          stage.
        - **'measured_temp_stderr'** (*float*) - The standard error in the measured
          temperature values of the nve stage.
        - **'rdf'** (*atomman.thermo.RDF*) - The RDF calculation object obtained
          from the dump files.
    """

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pressure = uc.set_in_units(pressure)
    rdf_minr = uc.set_in_units(rdf_minr)
    rdf_maxr = uc.set_in_units(rdf_maxr)

    # Run LAMMPS simulation
    results = liquid_npt(lmp, system, temperature, pressure=pressure,
                         temperature_melt=temperature_melt,
                         meltsteps=meltsteps, equilsteps=equilsteps,
                         runsteps=runsteps, dumpsteps=dumpsteps,
                         restartsteps=restartsteps, createvelocities=createvelocities,
                         randomseed=randomseed, usefiles=usefiles)

    # Compute RDF table based on dump files
    rdf = compute_ave_rdf(rdf_nbins, rdf_minr, rdf_maxr)
    results['rdf'] = rdf
    
    # Delete all but the last dump file
    if rdf_delete_dump:
        for dump_file in Path('.').glob('*.dump'):
            if dump_file.name != results['dumpfile_final']:
                dump_file.unlink()

    # Delete restart files now that calculation is finished
    for restart_file in Path('.').glob('*.restart'):
        restart_file.unlink()

    return results

def liquid_npt(lmp: LAMMPSobj,
               system: am.System,
               temperature: float,
               pressure: float = 0.0,
               temperature_melt: float = 3000.0,
               meltsteps: int = 50000,
               equilsteps: int = 20000,
               runsteps: int = 1000000,
               dumpsteps: Optional[int] = None,
               restartsteps: Optional[int] = None,
               createvelocities: bool = True,
               randomseed: Optional[int] = None,
               usefiles: bool = False) -> dict:
    """
    Runs the LAMMPS MD liquid relaxation simulation.

    Parameters
    ----------
    lmp : LAMMPSEXE or LAMMPSLIB
        An atomman LAMMPS interface object.
    system : atomman.System
        The atomic configuration to evaluate.
    temperature : float
        The target temperature to relax to.
    pressure : float, optional
        The target hydrostatic pressure to relax to. Default value is 0 GPa.
    temperature_melt : float, optional
        The elevated temperature to first use to hopefully melt the initial
        configuration during the meltsteps.
    meltsteps : int, optional
        The number of npt integration steps to perform at the melt temperature
        to create an amorphous liquid structure.  Default value is 50,000.
    equilsteps : int, optional
        The number of npt integration steps to perform at the target temperature
        and pressure prior to collecting the thermo and dump files for property
        evaluation.  Default value is 20,000.
    runsteps : int or None, optional
        The number of npt integration steps to perform at the target temperature
        and pressure where thermo and dump files are used for property
        evaluation.  Default value is 1,000,000.
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps during the runsteps
        simulation.  Note that these are used to compute the RDF curve rather
        than using the LAMMPS method to allow for larger RDF cutoffs.  Default
        value of None will use runsteps / 100.
    restartsteps : int or None, optional
        Restart files will be saved every this many steps.  Default is None,
        which will not create restart files.
    createvelocities : bool, optional
        If True (default), velocities will be created for the atoms prior to
        running the simulations.  Setting this to False can be useful if the
        initial system already has velocity information.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    usefiles : bool, optional
        If set to True, then all input/output files for LAMMPS will be generated.
        Default value of False will minimize the files created.

    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_final'** (*str*) - The name of the final dump file
          created.
        - **'symbols_final'** (*list*) - The symbols associated with the final
          dump file.
        - **'E_pot'** (*float*) - The mean measured potential energy during the energy
          equilibration stage.
        - **'E_pot_stderr'** (*float*) - The standard error in the mean potential energy
          during the energy equilibration stage.
        - **'E_total'** (*float*) - The total energy of the system used during the nve
          stage.
        - **'E_total_stderr'** (*float*) - The standard error in the mean total energy
          computed during the energy equilibration stage.
          - **'volume'** (*float*) - The volume per atom identified after the volume 
          equilibration stage.
        - **'volume_stderr'** (*float*) - The standard error in the volume per atom
          measured during the volume equilibration stage.
        - **'measured_press'** (*float*) - The mean measured pressure during the nve
          stage.
        - **'measured_press_stderr'** (*float*) - The standard error in the measured
          pressure values of the nve stage.
        - **'measured_temp'** (*float*) - The mean measured temperature during the nve
          stage.
        - **'measured_temp_stderr'** (*float*) - The standard error in the measured
          temperature values of the nve stage.
    """
    logfile = 'log.lammps'
    restartfile = '*.restart'

    if usefiles:
        script = 'liquid.in'
    else:
        script = None

    # Handle default values
    randomseed = am.lammps.seed(randomseed)
    if dumpsteps is None:
        dumpsteps = round(runsteps / 100)

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep
    pressure_damp = 1000 * timestep
    
    # Check if simulation is a restart
    isrestart = lmp.restart_check(logfile, restartfile)

    # Set up new simulation and run initial relaxations
    if not isrestart:

        # Pass system and potential info into LAMMPS
        lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                      usefiles=usefiles, logfile=logfile)
    
        # Set timestep
        lmp.cmd.timestep(timestep)

        # Define thermo
        lmp.cmd.thermo(100)
        lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                            'press', 'lx', 'ly', 'lz', 'vol')
        lmp.cmd.thermo_modify('format', 'float', '%.17e')

        # Create new velocities
        if createvelocities:
            if meltsteps == 0:
                velocity_temp = temperature
            else:
                velocity_temp = temperature_melt
            lmp.cmd.velocity('all', 'create', velocity_temp, randomseed, 'mom',
                            'yes', 'rot', 'yes', 'dist', 'gaussian')

        # Melt run
        lmp.cmd.fix('npt', 'all', 'npt',
                    'temp', temperature_melt, temperature_melt, temperature_damp,
                    'iso', pressure, pressure, pressure_damp)
        lmp.cmd.run(meltsteps)
        lmp.cmd.unfix('npt')

        # Equilibrium run
        lmp.cmd.fix('npt', 'all', 'npt',
                    'temp', temperature, temperature, temperature_damp,
                    'iso', pressure, pressure, pressure_damp)
        lmp.cmd.run(equilsteps)
        lmp.cmd.unfix('npt')

        # Reset timestep before main run
        lmp.cmd.reset_timestep(0)

    # Set up restart simulation
    else:
        # Tell LAMMPS to read in from restart and redefine potential
        lmp.new_system_from_restart(system, restartfile, tilt_large=True,
                                    usefiles=True, logfile=logfile)

        # Define thermo
        lmp.cmd.thermo(100)
        lmp.cmd.thermo_style('custom', 'step', 'temp', 'pe', 'ke', 'etotal',
                            'press', 'lx', 'ly', 'lz', 'vol')
        lmp.cmd.thermo_modify('format', 'float', '%.17e')
    

    # Set up analysis computes
    lmp.cmd.compute('pe', 'all', 'pe/atom')

    # Dump configurations
    if lmp.potential.atom_style == 'charge':
        dump_keys = ['id', 'type', 'q', 'xu', 'yu', 'zu', 'c_pe', 'vx', 'vy', 'vz']
    else:
        dump_keys = ['id', 'type', 'xu', 'yu', 'zu', 'c_pe', 'vx', 'vy', 'vz']
    lmp.cmd.dump('dumpit', 'all', 'custom', dumpsteps, '*.dump', *dump_keys)
    lmp.cmd.dump_modify('dumpit', 'format', 'float', '%.17e')
    
    # Restart configurations
    if restartsteps is not None:
        lmp.cmd.restart(restartsteps, restartfile)

    # Perform npt at target temperature and pressure
    lmp.cmd.fix('npt', 'all', 'npt',
                'temp', temperature, temperature, temperature_damp,
                'iso', pressure, pressure, pressure_damp)
    lmp.cmd.run(runsteps, 'upto')

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

    # Get combined thermo data of primary simulation(s).
    thermo = log.flatten('last', firstindex=2).thermo
    lmp.set_thermo_units(thermo)

    results = {}

    # Set final dumpfile info
    last_dump_number = 0
    for dump_file in Path('.').glob('*.dump'):
        dump_number = int(dump_file.name[:-5])
        if dump_number > last_dump_number:
            last_dump_number = dump_number
    last_dump_file = f'{last_dump_number}.dump'
    results['dumpfile_final'] = last_dump_file
    results['symbols_final'] = system.symbols

    # Get ave/stderr thermo properties
    nsamples = len(thermo)
    sqrt_nsamples = nsamples ** 0.5
    
    natoms = system.natoms
    results['E_pot'] = thermo.PotEng.mean() / natoms
    results['E_pot_stderr'] = thermo.PotEng.std() / natoms / sqrt_nsamples
    results['E_total'] = thermo.TotEng.mean() / natoms
    results['E_total_stderr'] = thermo.TotEng.std() / natoms / sqrt_nsamples
    results['volume'] = thermo.Volume.mean() / natoms
    results['volume_stderr'] = thermo.Volume.std() / natoms / sqrt_nsamples
    results['measured_press'] = thermo.Press.mean()
    results['measured_press_stderr'] = thermo.Press.std() / sqrt_nsamples
    results['measured_temp'] = thermo.Temp.mean()
    results['measured_temp_stderr'] = thermo.Temp.std() / sqrt_nsamples

    return results


def compute_ave_rdf(nbins=400, rmin=0.0, rmax=10.0) -> am.thermo.RDF:
    """
    Computes the averaged RDF across the dump files and saves the
    data to a LAMMPS-style RDF text file.

    Parameters
    ----------
    nbins : int, optional
        The number of bins to use for the RDF calculation.  Default value is
        400.
    minr : float or str, optional
        The minimum radial distance for the RDF calculation.  Default value
        is 0.0 angstroms.
    maxr: float or str, optional
        The mxaimum radial distance for the RDF calculation.  Default value
        is 10.0 angstroms.

    Returns
    -------
    atomman.thermo.RDF
        The RDF object
    """
    # Load dump files and compute RDFs
    rdfs = []
    for dumpfile in Path('.').glob('*.dump'):
        system = am.load('atom_dump', dumpfile)
        rdfs.append(system.rdf(nbins=nbins, rmin=rmin, rmax=rmax))
    
    # Average the rdfs
    rdf = RDF.average(rdfs)

    # Save the averaged RDF file
    rdf.build_lammps_file('rdf_dump.txt')

    return rdf
