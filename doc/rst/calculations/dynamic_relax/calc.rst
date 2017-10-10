
calc_dynamic_relax.py
*********************


Calculation script functions
============================

**full_relax(lammps_command, system, potential, symbols,
mpi_command=None, ucell=None, p_xx=0.0, p_yy=0.0, p_zz=0.0,
temperature=0.0, integrator=None, runsteps=220000, thermosteps=100,
dumpsteps=None, equilsteps=20000, randomseed=None)**

   Performs a full dynamic relax on a given system at the given
   temperature to the specified pressure state.

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **mpi_command** (*str**, **optional*) -- The MPI command for
        running LAMMPS in parallel.  If not given, LAMMPS will run
        serially.

      * **ucell** (*atomman.System**, **optional*) -- The fundamental
        unit cell correspodning to system.  This is used to convert
        system dimensions to cell dimensions. If not given, ucell will
        be taken as system.

      * **p_xx** (*float**, **optional*) -- The value to relax the x
        tensile pressure component to (default is 0.0).

      * **p_yy** (*float**, **optional*) -- The value to relax the y
        tensile pressure component to (default is 0.0).

      * **p_zz** (*float**, **optional*) -- The value to relax the z
        tensile pressure component to (default is 0.0).

      * **temperature** (*float**, **optional*) -- The temperature to
        relax at (default is 0.0).

      * **runsteps** (*int**, **optional*) -- The number of
        integration steps to perform (default is 220000).

      * **integrator** (*str** or **None**, **optional*) -- The
        integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin
        thermostat. (Default is None, which will use 'nph+l' for
        temperature == 0, and 'npt' otherwise.)

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

      * **'a_lat'** (*float*) - The mean measured a lattice constant.

      * **'b_lat'** (*float*) - The mean measured b lattice constant.

      * **'c_lat'** (*float*) - The mean measured c lattice constant.

      * **'alpha_lat'** (*float*) - The alpha lattice angle.

      * **'beta_lat'** (*float*) - The beta lattice angle.

      * **'gamma_lat'** (*float*) - The gamma lattice angle.

      * **'E_coh'** (*float*) - The mean measured cohesive energy.

      * **'stress'** (*numpy.array*) - The mean measured stress state.

      * **'temp'** (*float*) - The mean measured temperature.

      * **'a_lat_std'** (*float*) - The standard deviation in the
        measured a lattice constant values.

      * **'b_lat_std'** (*float*) - The standard deviation in the
        measured b lattice constant values.

      * **'c_lat_std'** (*float*) - The standard deviation in the
        measured c lattice constant values.

      * **'E_coh_std'** (*float*) - The standard deviation in the
        measured cohesive energy values.

      * **'stress_std'** (*numpy.array*) - The standard deviation in
        the measured stress state values.

      * **'temp_std'** (*float*) - The standard deviation in the
        measured temperature values.

   :Return type:
      dict

**integrator_info(integrator=None, p_xx=0.0, p_yy=0.0, p_zz=0.0,
temperature=0.0, randomseed=None, units='metal')**

   Generates LAMMPS commands for velocity creation and fix
   integrators.

   :Parameters:
      * **integrator** (*str** or **None**, **optional*) -- The
        integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin
        thermostat. (Default is None, which will use 'nph+l' for
        temperature == 0, and 'npt' otherwise.)

      * **p_xx** (*float**, **optional*) -- The value to relax the x
        tensile pressure component to (default is 0.0).

      * **p_yy** (*float**, **optional*) -- The value to relax the y
        tensile pressure component to (default is 0.0).

      * **p_zz** (*float**, **optional*) -- The value to relax the z
        tensile pressure component to (default is 0.0).

      * **temperature** (*float**, **optional*) -- The temperature to
        relax at (default is 0.0).

      * **randomseed** (*int** or **None**, **optional*) -- Random
        number seed used by LAMMPS in creating velocities and with the
        Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)

      * **units** (*str**, **optional*) -- The LAMMPS units style to
        use (default is 'metal').

   :Returns:
      The generated LAMMPS input lines for velocity create and fix
      integration commands.

   :Return type:
      str

**main(*args)**

   Main function called when script is executed directly.

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
