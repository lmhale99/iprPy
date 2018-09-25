
calc_relax_dynamic.py
*********************


Calculation script functions
============================

**integrator_info(integrator=None, p_xx=0.0, p_yy=0.0, p_zz=0.0,
p_xy=0.0, p_xz=0.0, p_yz=0.0, temperature=0.0, randomseed=None,
units='metal')**

   Generates LAMMPS commands for velocity creation and fix
   integrators.

   :Parameters:
      * **integrator** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_* or
        *`None
        <https://docs.python.org/3/library/constants.html#None>`_*,
        **optional*) – The integration method to use. Options are
        ‘npt’, ‘nvt’, ‘nph’, ‘nve’, ‘nve+l’, ‘nph+l’. The +l options
        use Langevin thermostat. (Default is None, which will use
        ‘nph+l’ for temperature == 0, and ‘npt’ otherwise.)

      * **p_xx** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the x tensile pressure
        component to (default is 0.0).

      * **p_yy** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the y tensile pressure
        component to (default is 0.0).

      * **p_zz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the z tensile pressure
        component to (default is 0.0).

      * **p_xy** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the xy shear pressure
        component to (default is 0.0).

      * **p_xz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the xz shear pressure
        component to (default is 0.0).

      * **p_yz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the yz shear pressure
        component to (default is 0.0).

      * **temperature** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The temperature to relax at (default is 0.0).

      * **randomseed** (`int
        <https://docs.python.org/3/library/functions.html#int>`_* or
        *`None
        <https://docs.python.org/3/library/constants.html#None>`_*,
        **optional*) – Random number seed used by LAMMPS in creating
        velocities and with the Langevin thermostat.  (Default is None
        which will select a random int between 1 and 900000000.)

      * **units** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The LAMMPS units style to use (default is
        ‘metal’).

   :Returns:
      The generated LAMMPS input lines for velocity create and fix
      integration commands.

   :Return type:
      `str <https://docs.python.org/3/library/stdtypes.html#str>`_

**main(*args)**

   Main function called when script is executed directly.

**process_input(input_dict, UUID=None, build=True)**

   Processes str input parameters, assigns default values if needed,
   and generates new, more complex terms as used by the calculation.

   :Parameters:
      * **input_dict** (`dict
        <https://docs.python.org/3/library/stdtypes.html#dict>`_) –
        Dictionary containing the calculation input parameters with
        string values.  The allowed keys depends on the calculation
        style.

      * **UUID** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – Unique identifier to use for the calculation
        instance.  If not given and a ‘UUID’ key is not in input_dict,
        then a random UUID4 hash tag will be assigned.

      * **build** (`bool
        <https://docs.python.org/3/library/functions.html#bool>`_*,
        **optional*) – Indicates if all complex terms are to be built.
        A value of False allows for default values to be assigned even
        if some inputs required by the calculation are incomplete.
        (Default is True.)

**relax_dynamic(lammps_command, system, potential, mpi_command=None,
p_xx=0.0, p_yy=0.0, p_zz=0.0, p_xy=0.0, p_xz=0.0, p_yz=0.0,
temperature=0.0, integrator=None, runsteps=220000, thermosteps=100,
dumpsteps=None, equilsteps=20000, randomseed=None)**

   Performs a full dynamic relax on a given system at the given
   temperature to the specified pressure state.

   :Parameters:
      * **lammps_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_) –
        Command for running LAMMPS.

      * **system** (*atomman.System*) – The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) – The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) – The list of element-model
        symbols for the Potential that correspond to system’s atypes.

      * **mpi_command** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_*,
        **optional*) – The MPI command for running LAMMPS in parallel.
        If not given, LAMMPS will run serially.

      * **p_xx** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the x tensile pressure
        component to (default is 0.0).

      * **p_yy** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the y tensile pressure
        component to (default is 0.0).

      * **p_zz** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The value to relax the z tensile pressure
        component to (default is 0.0).

      * **temperature** (`float
        <https://docs.python.org/3/library/functions.html#float>`_*,
        **optional*) – The temperature to relax at (default is 0.0).

      * **runsteps** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – The number of integration steps to perform
        (default is 220000).

      * **integrator** (`str
        <https://docs.python.org/3/library/stdtypes.html#str>`_* or
        *`None
        <https://docs.python.org/3/library/constants.html#None>`_*,
        **optional*) – The integration method to use. Options are
        ‘npt’, ‘nvt’, ‘nph’, ‘nve’, ‘nve+l’, ‘nph+l’. The +l options
        use Langevin thermostat. (Default is None, which will use
        ‘nph+l’ for temperature == 0, and ‘npt’ otherwise.)

      * **thermosteps** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – Thermo values will be reported every this many
        steps (default is 100).

      * **dumpsteps** (`int
        <https://docs.python.org/3/library/functions.html#int>`_* or
        *`None
        <https://docs.python.org/3/library/constants.html#None>`_*,
        **optional*) – Dump files will be saved every this many steps
        (default is None, which sets dumpsteps equal to runsteps).

      * **equilsteps** (`int
        <https://docs.python.org/3/library/functions.html#int>`_*,
        **optional*) – The number of timesteps at the beginning of the
        simulation to exclude when computing average values (default
        is 20000).

      * **randomseed** (`int
        <https://docs.python.org/3/library/functions.html#int>`_* or
        *`None
        <https://docs.python.org/3/library/constants.html#None>`_*,
        **optional*) – Random number seed used by LAMMPS in creating
        velocities and with the Langevin thermostat.  (Default is None
        which will select a random int between 1 and 900000000.)

   :Returns:
      Dictionary of results consisting of keys:

      * **’relaxed_system’** (*float*) - The relaxed system.

      * **’E_coh’** (*float*) - The mean measured cohesive energy.

      * **’measured_pxx’** (*float*) - The measured x tensile pressure
        of the relaxed system.

      * **’measured_pyy’** (*float*) - The measured y tensile pressure
        of the relaxed system.

      * **’measured_pzz’** (*float*) - The measured z tensile pressure
        of the relaxed system.

      * **’measured_pxy’** (*float*) - The measured xy shear pressure
        of the relaxed system.

      * **’measured_pxz’** (*float*) - The measured xz shear pressure
        of the relaxed system.

      * **’measured_pyz’** (*float*) - The measured yz shear pressure
        of the relaxed system.

      * **’temp’** (*float*) - The mean measured temperature.

      * **’E_coh_std’** (*float*) - The standard deviation in the
        measured cohesive energy values.

      * **’measured_pxx_std’** (*float*) - The standard deviation in
        the measured x tensile pressure of the relaxed system.

      * **’measured_pyy_std’** (*float*) - The standard deviation in
        the measured y tensile pressure of the relaxed system.

      * **’measured_pzz_std’** (*float*) - The standard deviation in
        the measured z tensile pressure of the relaxed system.

      * **’measured_pxy_std’** (*float*) - The standard deviation in
        the measured xy shear pressure of the relaxed system.

      * **’measured_pxz_std’** (*float*) - The standard deviation in
        the measured xz shear pressure of the relaxed system.

      * **’measured_pyz_std’** (*float*) - The standard deviation in
        the measured yz shear pressure of the relaxed system.

      * **’temp_std’** (*float*) - The standard deviation in the
        measured temperature values.

   :Return type:
      `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_
