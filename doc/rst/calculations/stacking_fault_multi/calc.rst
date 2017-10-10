
calc_stacking_fault_multi.py
****************************


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

**stackingfaultmap(lammps_command, system, potential, symbols,
shiftvector1, shiftvector2, mpi_command=None, numshifts1=11,
numshifts2=11, cutboxvector=None, faultpos=0.5, etol=0.0, ftol=0.0,
maxiter=10000, maxeval=100000, dmax=0.01)**

   Computes a generalized stacking fault map for shifts along a
   regular 2D grid.

   :Parameters:
      * **lammps_command** (*str*) -- Command for running LAMMPS.

      * **system** (*atomman.System*) -- The system to perform the
        calculation on.

      * **potential** (*atomman.lammps.Potential*) -- The LAMMPS
        implemented potential to use.

      * **symbols** (*list of str*) -- The list of element-model
        symbols for the Potential that correspond to system's atypes.

      * **shiftvector1** (*list of floats** or **numpy.array*) -- One
        of the generalized stacking fault shifting vectors.

      * **shiftvector2** (*list of floats** or **numpy.array*) -- One
        of the generalized stacking fault shifting vectors.

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

      * **numshifts1** (*int**, **optional*) -- The number of equally
        spaced shiftfractions to evaluate along shiftvector1.

      * **numshifts2** (*int**, **optional*) -- The number of equally
        spaced shiftfractions to evaluate along shiftvector2.

   :Returns:
      Dictionary of results consisting of keys:

      * **'shift1'** (*numpy.array of float*) - The fractional shifts
        along shiftvector1 where the stacking fault was evaluated.

      * **'shift2'** (*numpy.array of float*) - The fractional shifts
        along shiftvector2 where the stacking fault was evaluated.

      * **'E_gsf'** (*numpy.array of float*) - The stacking fault
        formation energies measured for all the (shift1, shift2)
        coordinates.

      * **'delta_disp'** (*numpy.array of float*) - The change in the
        center of mass difference between before and after applying
        the faultshift for all the (shift1, shift2) coordinates.

      * **'A_fault'** (*float*) - The area of the fault surface.

   :Return type:
      dict

**stackingfaultpoint(lammps_command, system, potential, symbols,
mpi_command=None, sim_directory=None, cutboxvector='c', faultpos=0.5,
faultshift=[0.0, 0.0, 0.0], etol=0.0, ftol=0.0, maxiter=10000,
maxeval=100000, dmax=0.01, lammps_date=None)**

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

      * **lammps_date** (*datetime.date** or **None**, **optional*) --
        The date version of the LAMMPS executable.  If None, will be
        identified from the lammps_command (default is None).

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

**stackingfaultworker(lammps_command, system, potential, symbols,
shiftvector1, shiftvector2, shiftfraction1, shiftfraction2,
mpi_command=None, cutboxvector=None, faultpos=0.5, etol=0.0, ftol=0.0,
maxiter=10000, maxeval=100000, dmax=0.01, lammps_date=None)**

   A wrapper function around stackingfaultpoint. Converts
   shiftfractions and shiftvectors to a faultshift, runs
   stackingfaultpoint, and adds keys 'shift1' and 'shift2' to the
   returned dictionary corresponding to the shiftfractions.
