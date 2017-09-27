
calc_E_vs_r_scan.py
*******************


Calculation script functions
============================

**e_vs_r(lammps_command, system, potential, symbols, mpi_command=None,
ucell=None, rmin=2.0, rmax=6.0, rsteps=200)**

   Performs a cohesive energy scan over a range of interatomic spaces,
   r.

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

      * **rmin** (*float**, **optional*) -- The minimum r spacing to
        use (default value is 2.0 angstroms).

      * **rmax** (*float**, **optional*) -- The maximum r spacing to
        use (default value is 6.0 angstroms).

      * **rsteps** (*int**, **optional*) -- The number of r spacing
        steps to evaluate (default value is 200).

   :Returns:
      Dictionary of results consisting of keys:

      * **'r_values'** (*numpy.array of float*) - All interatomic
        spacings, r, explored.

      * **'a_values'** (*numpy.array of float*) - All unit cell a
        lattice constants corresponding to the values explored.

      * **'Ecoh_values'** (*numpy.array of float*) - The computed
        cohesive energies for each r value.

      * **'min_cell'** (*list of atomman.System*) - Systems
        corresponding to the minima identified in the Ecoh_values.

   :Return type:
      dict

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

**r_a_ratio(ucell)**

   Calculates the r/a ratio by identifying the shortest interatomic
   spacing, r, for a unit cell.

   :Parameters:
      **ucell** (*atomman.System*) -- The unit cell system to
      evaluate.

   :Returns:
      The shortest interatomic spacing, r, divided by the unit cell's
      a lattice parameter.

   :Return type:
      float
