
calc_point_defect_diffusion.py
******************************


Calculation script functions
============================

**main(*args)**

   Main function called when script is executed directly.

**pointdiffusion(lammps_command, system, potential, symbols,
point_kwargs, mpi_command=None, temperature=300, runsteps=100000,
thermosteps=None, dumpsteps=None, equilsteps=20000, randomseed=None)**

   Evaluates the diffusion rate of a point defect at a given
   temperature. This method will run two simulations: an NVT run at
   the specified temperature to equilibrate the system, then an NVE
   run to measure the defect's diffusion rate. The diffusion rate is
   evaluated using the mean squared displacement of all atoms in the
   system, and using the assumption that diffusion is only due to the
   added defect(s).

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **point_kwargs** (*dict** or **list of dict*) -- One or more
        dictionaries containing the keyword arguments for the
        atomman.defect.point() function to generate specific point
        defect configuration(s).

      * **mpi_command** (*str**, **optional*) -- The MPI command for
        running LAMMPS in parallel.  If not given, LAMMPS will run
        serially.

      * **temperature** (*float**, **optional*) -- The temperature to
        run at (default is 300.0).

      * **runsteps** (*int**, **optional*) -- The number of
        integration steps to perform (default is 100000).

      * **thermosteps** (*int**, **optional*) -- Thermo values will be
        reported every this many steps (default is 100).

      * **dumpsteps** (*int** or **None**, **optional*) -- Dump files
        will be saved every this many steps (default is None, which
        sets dumpsteps equal to runsteps).

      * **equilsteps** (*int**, **optional*) -- The number of
        timesteps at the beginning of the simulation to exclude when
        computing average values (default is 20000).

      * **randomseed** (*int** or **None**, **optional*) -- Random
        number seed used by LAMMPS in creating velocities and with the
        Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)

   :Returns:
      Dictionary of results consisting of keys:

      * **'natoms'** (*int*) - The number of atoms in the system.

      * **'temp'** (*float*) - The mean measured temperature.

      * **'pxx'** (*float*) - The mean measured normal xx pressure.

      * **'pyy'** (*float*) - The mean measured normal yy pressure.

      * **'pzz'** (*float*) - The mean measured normal zz pressure.

      * **'Epot'** (*numpy.array*) - The mean measured total potential
        energy.

      * **'temp_std'** (*float*) - The standard deviation in the
        measured temperature values.

      * **'pxx_std'** (*float*) - The standard deviation in the
        measured normal xx pressure values.

      * **'pyy_std'** (*float*) - The standard deviation in the
        measured normal yy pressure values.

      * **'pzz_std'** (*float*) - The standard deviation in the
        measured normal zz pressure values.

      * **'Epot_std'** (*float*) - The standard deviation in the
        measured total potential energy values.

      * **'dx'** (*float*) - The computed diffusion constant along the
        x-direction.

      * **'dy'** (*float*) - The computed diffusion constant along the
        y-direction.

      * **'dz'** (*float*) - The computed diffusion constant along the
        y-direction.

      * **'d'** (*float*) - The total computed diffusion constant.

   :Return type:
      dict

**process_input(input_dict, UUID=None, build=True)**

   Processes str input parameters, assigns default values if needed,
   and generates new, more complex terms as used by the calculation.

   :Parameters:
      * **input_dict** (*dict*) -- Dictionary containing the
        calculation input parameters with string values.  The allowed
        keys depends on the calculation style.

      * **UUID** (*str**, **optional*) -- Unique identifier to use for
        the calculation instance.  If not given and a 'UUID' key is
        not in input_dict, then a random UUID4 hash tag will be
        assigned.

      * **build** (*bool**, **optional*) -- Indicates if all complex
        terms are to be built.  A value of False allows for default
        values to be assigned even if some inputs required by the
        calculation are incomplete.  (Default is True.)
