isolated_atom Input Terms
=========================

Calculation Metadata
--------------------

Specifies metadata descriptors common to all calculation styles.

-  **branch**: A metadata group name that the calculation can be parsed
   by. Primarily meant for differentiating runs with different settings
   parameters.

LAMMPS and MPI Commands
-----------------------

Specifies the external commands for running LAMMPS and MPI.

-  **lammps_command**: The path to the executable for running LAMMPS on
   your system. Don’t include command line options.
-  **mpi_command**: The path to the MPI executable and any command line
   options to use for calling LAMMPS to run in parallel on your system.
   LAMMPS will run as a serial process if not given.

Interatomic Potential
---------------------

Specifies the interatomic potential to use and the directory where any
associated parameter files are located.

-  **potential_file**: The path to the potential_LAMMPS or
   potential_LAMMPS_KIM record that defines the interatomic potential to
   use for LAMMPS calculations.
-  **potential_kim_id**: If potential_file is a potential_LAMMPS_KIM
   record, this allows for the specification of which version of the KIM
   model to use by specifying a full kim model id. If not given, the
   newest known version of the kim model will be assumed.
-  **potential_kim_potid**: Some potential_LAMMPS_KIM records are
   associated with multiple potential entries. This allows for the clear
   specification of which potential (by potid) to associate with those
   kim models.This will affect the list of available symbols for the
   calculation.
-  **potential_dir**: The path to the directory containing any potential
   parameter files (eg. eam.alloy setfl files) that are needed for the
   potential. If not given, then any required files are expected to be
   in the working directory where the calculation is executed.

Input/Output Units
------------------

Specifies the default units to use for the other input keys and to use
for saving to the results file.

-  **length_unit**: The unit of length to use. Default value is
   ‘angstrom’.
-  **pressure_unit**: The unit of pressure to use. Default value is
   ‘GPa’.
-  **energy_unit**: The unit of energy to use. Default value is ‘eV’.
-  **force_unit**: The unit of force to use. Default value is
   ‘eV/angstrom’.
