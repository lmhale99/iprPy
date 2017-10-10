
calc_stacking_fault.py
**********************


Calculation script functions
============================

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

**stackingfault(lammps_command, system, potential, symbols,
mpi_command=None, cutboxvector=None, faultpos=0.5, faultshift=[0.0,
0.0, 0.0], etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
dmax=0.01)**

   Computes the generalized stacking fault value for a single
   faultshift.

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

      * **etol** (*float**, **optional*) -- The energy tolerance for
        the structure minimization. This value is unitless. (Default
        is 0.0).

      * **ftol** (*float**, **optional*) -- The force tolerance for
        the structure minimization. This value is in units of force.
        (Default is 0.0).

      * **maxiter** (*int**, **optional*) -- The maximum number of
        minimization iterations to use (default is 10000).

      * **maxeval** (*int**, **optional*) -- The maximum number of
        minimization evaluations to use (default is 100000).

      * **dmax** (*float**, **optional*) -- The maximum distance in
        length units that any atom is allowed to relax in any
        direction during a single minimization iteration (default is
        0.01 Angstroms).

      * **cutboxvector** (*str**, **optional*) -- Indicates which of
        the three system box vectors, 'a', 'b', or 'c', to cut with a
        non-periodic boundary (default is 'c').

      * **faultpos** (*float**, **optional*) -- The fractional
        position along the cutboxvector where the stacking fault plane
        will be placed (default is 0.5).

      * **faultshift** (*list of float**, **optional*) -- The vector
        shift to apply to all atoms above the fault plane defined by
        faultpos (default is [0,0,0], i.e. no shift applied).

   :Returns:
      Dictionary of results consisting of keys:

      * **'E_gsf'** (*float*) - The stacking fault formation energy.

      * **'E_total_0'** (*float*) - The total potential energy of the
        system before applying the faultshift.

      * **'E_total_sf'** (*float*) - The total potential energy of the
        system after applying the faultshift.

      * **'delta_disp'** (*float*) - The change in the center of mass
        difference between before and after applying the faultshift.

      * **'disp_0'** (*float*) - The center of mass difference between
        atoms above and below the fault plane in the cutboxvector
        direction for the system before applying the faultshift.

      * **'disp_sf'** (*float*) - The center of mass difference
        between atoms above and below the fault plane in the
        cutboxvector direction for the system after applying the
        faultshift.

      * **'A_fault'** (*float*) - The area of the fault surface.

      * **'dumpfile_0'** (*str*) - The name of the LAMMMPS dump file
        associated with the relaxed system before applying the
        faultshift.

      * **'dumpfile_sf'** (*str*) - The name of the LAMMMPS dump file
        associated with the relaxed system after applying the
        faultshift.

   :Return type:
      dict

**stackingfaultpoint(lammps_command, system, potential, symbols,
mpi_command=None, sim_directory=None, cutboxvector='c', faultpos=0.5,
faultshift=[0.0, 0.0, 0.0], etol=0.0, ftol=0.0, maxiter=10000,
maxeval=100000, dmax=0.01)**

   Perform a stacking fault relaxation simulation for a single
   faultshift.

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

      * **sim_directory** (*str**, **optional*) -- The path to the
        directory to perform the simuation in.  If not given, will use
        the current working directory.

      * **etol** (*float**, **optional*) -- The energy tolerance for
        the structure minimization. This value is unitless. (Default
        is 0.0).

      * **ftol** (*float**, **optional*) -- The force tolerance for
        the structure minimization. This value is in units of force.
        (Default is 0.0).

      * **maxiter** (*int**, **optional*) -- The maximum number of
        minimization iterations to use (default is 10000).

      * **maxeval** (*int**, **optional*) -- The maximum number of
        minimization evaluations to use (default is 100000).

      * **dmax** (*float**, **optional*) -- The maximum distance in
        length units that any atom is allowed to relax in any
        direction during a single minimization iteration (default is
        0.01 Angstroms).

      * **cutboxvector** (*str**, **optional*) -- Indicates which of
        the three system box vectors, 'a', 'b', or 'c', to cut with a
        non-periodic boundary (default is 'c').

      * **faultpos** (*float**, **optional*) -- The fractional
        position along the cutboxvector where the stacking fault plane
        will be placed (default is 0.5).

      * **faultshift** (*list of float**, **optional*) -- The vector
        shift to apply to all atoms above the fault plane defined by
        faultpos (default is [0,0,0], i.e. no shift applied).

   :Returns:
      Dictionary of results consisting of keys:

      * **'logfile'** (*str*) - The filename of the LAMMPS log file.

      * **'dumpfile'** (*str*) - The filename of the LAMMPS dump file
        of the relaxed system.

      * **'system'** (*atomman.System*) - The relaxed system.

      * **'A_fault'** (*float*) - The area of the fault surface.

      * **'E_total'** (*float*) - The total potential energy of the
        relaxed system.

      * **'disp'** (*float*) - The center of mass difference between
        atoms above and below the fault plane in the cutboxvector
        direction.

   :Return type:
      dict

   :Raises:
      ``ValueError`` -- For invalid cutboxvectors.
