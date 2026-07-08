# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj

def thermal_conductivity_direct(lammps_command: Union[str, LAMMPSobj],
                                system: am.System,
                                potential: lammpspotential,
                                mpi_command: Optional[str] = None,
                                timestep: Optional[unitfloat] = None,
                                equilsteps: int = 0,
                                temperature: Optional[float] = None,
                                runsteps: int = 2000,
                                simruns: int = 100,
                                centroid_stress: bool = False,
                                createvelocities: bool = False,
                                randomseed: Optional[int] = None,
                                usefiles: bool = False) -> dict:

    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    logfile = 'log.lammps'
    if usefiles or not lmp.islib:
        script = 'kappa.in'
    else:
        script = None

    # Check/select a randomseed value
    randomseed = am.lammps.seed(randomseed)

    # Set timestep in atomman and LAMMPS units
    if timestep is None:
        timestep_lammps = am.lammps.style.timestep(lmp.potential.units)
        timestep = uc.set_in_units(timestep_lammps, lmp.unitsdict['time'])
    else:
        timestep = uc.set_in_units(timestep)
        timestep_lammps = uc.get_in_units(timestep, lmp.unitsdict['time'])
    temperature_damp = 100 * timestep_lammps

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)

    lmp.commands_string('\n# Set the timestep')
    lmp.cmd.timestep(timestep_lammps)

    # Optional equilibrium run
    if equilsteps > 0:
        assert temperature is not None

        if createvelocities:
            lmp.commands_string('\n# Create new velocities')
            lmp.cmd.velocity('all', 'create', temperature, randomseed, 'mom',
                            'yes', 'rot', 'yes', 'dist', 'gaussian')
        
        lmp.commands_string('\n# Equilibration run')
        lmp.cmd.fix('NVT', 'all', 'nvt', 'temp', temperature, temperature, temperature_damp)
        lmp.cmd.run(equilsteps)
        lmp.cmd.unfix('NVT')
        lmp.cmd.reset_timestep(0)


    

