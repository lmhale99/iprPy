Input script parameters
-----------------------

This is a list of the input parameter names recognized by
calc_diatom_scan.py.

Global metadata parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **branch**: assigns a group/branch descriptor to the calculation
   which can help with parsing results later. Default value is ‘main’.

Command lines for LAMMPS and MPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the external commands for running LAMMPS and MPI.

-  **lammps_command**: the path to the executable for running LAMMPS on
   your system. Don’t include command line options.
-  **mpi_command**: the path to the MPI executable and any command line
   options to use for calling LAMMPS to run in parallel on your system.
   Default value is None (run LAMMPS as a serial process).

Potential definition and directory containing associated files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the information associated with an interatomic potential
implemented for LAMMPS.

-  **potential_file**: the path to the potential_LAMMPS data model used
   by atomman to generate the proper LAMMPS commands for an interatomic
   potential.
-  **potential_dir**: the path to the directory containing any potential
   artifacts (eg. eam.alloy setfl files) that are used. If not given,
   then any required files are expected to be in the working directory
   where the calculation is executed.

Units for input/output values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the units for various physical quantities to use when saving
values to the results record file. Also used as the default units for
parameters in this input parameter file.

-  **length_unit**: defines the unit of length for results, and input
   parameters if not directly specified. Default value is ‘angstrom’.
-  **energy_unit**: defines the unit of energy for results, and input
   parameters if not directly specified. Default value is ‘eV’.
-  **pressure_unit**: defines the unit of pressure for results, and
   input parameters if not directly specified. Default value is ‘GPa’.
-  **force_unit**: defines the unit of pressure for results, and input
   parameters if not directly specified. Default value is ‘eV/angstrom’.

Run Parameters
~~~~~~~~~~~~~~

Provides parameters specific to the calculation at hand.

-  **symbols**: the one or two model symbols to perform the scan for
-  **minimum_r**: specifies the minimum interatomic spacing, r, for the
   scan. Default value is ‘0.02 angstrom’.
-  **maximum_r**: specifies the maximum interatomic spacing, r, for the
   scan. Default value is ‘6.0 angstrom’.
-  **number_of_steps_r**: specifies the number of interatomic spacing
   values, r, to use. Default value is 300.
