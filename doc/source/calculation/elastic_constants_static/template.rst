elastic_constants_static Input Terms
====================================

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

Initial System Configuration
----------------------------

Specifies the file and options to load for the initial atomic
configuration.

-  **load_file**: The path to the initial configuration file to load.
-  **load_style**: The atomman.load() style indicating the format of the
   load_file.
-  **load_options**: A space-delimited list of key-value pairs for
   optional style-specific arguments used by atomman.load().
-  **family**: A metadata descriptor for relating the load_file back to
   the original crystal structure or prototype that the load_file was
   based on. If not given, will use the family field in load_file if
   load_style is ‘system_model’, or the file’s name otherwise.
-  **symbols**: A space-delimited list of the potential’s atom-model
   symbols to associate with the loaded system’s atom types. Required if
   load_file does not contain symbol/species information.
-  **box_parameters**: Specifies new box parameters to scale the loaded
   configuration by. Can be given either as a list of three or six
   numbers: ‘a b c’ for orthogonal boxes, or ‘a b c alpha beta gamma’
   for triclinic boxes. The a, b, c parameters are in units of length
   and the alpha, beta, gamma angles are in degrees.

System Manipulations
--------------------

Performs simple manipulations on the loaded initial system.

-  **a_uvw**: The Miller(-Bravais) crystal vector relative to the loaded
   system to orient with the a box vector of a resulting rotated system.
   Specified as three or four space-delimited numbers. Either all or
   none of the uvw parameters must be given.
-  **b_uvw**: The Miller(-Bravais) crystal vector relative to the loaded
   system to orient with the b box vector of a resulting rotated system.
   Specified as three or four space-delimited numbers. Either all or
   none of the uvw parameters must be given.
-  **c_uvw**: The Miller(-Bravais) crystal vector relative to the loaded
   system to orient with the c box vector of a resulting rotated system.
   Specified as three or four space-delimited numbers. Either all or
   none of the uvw parameters must be given.
-  **atomshift**: A rigid-body shift vector to apply to all atoms in the
   rotated configuration. Specified as three space-delimited numbers
   that are relative to the size of the system after rotating, but
   before sizemults have been applied. This allows for the same relative
   shift of similar systems regardless of box_parameters and sizemults.
   Default value is ‘0.0 0.0 0.0’ (i.e. no shift).
-  **sizemults**: Multiplication parameters to construct a supercell
   from the rotated system. Given as either three or six space-delimited
   integers. For three integers, each value indicates the number of
   replicas to make along the corresponding a, b, c box vector with
   negative values replicating in the negative Cartesian space. For six
   integers, the values are divided into three pairs with each pair
   indicating the number of ‘negative’ and ‘positive’ replications to
   make for a given a, b, c box vector.

LAMMPS Energy/Force Minimization
--------------------------------

Specifies the parameters and options associated with performing an
energy and/or force minimization in LAMMPS.

-  **energytolerance**: The energy tolerance to use for the
   minimization. This value is unitless and corresponds to the etol term
   for the LAMMPS minimize command. Default value is 0.0.
-  **forcetolerance**: The force tolerance to use for the minimization.
   This value is in force units and corresponds to the ftol term for the
   LAMMPS minimize command. Default value is ‘0.0 eV/angstrom’.
-  **maxiterations**: The maximum number of iterations to use for the
   minimization. This value corresponds to the maxiter term for the
   LAMMPS minimize command. Default value is 100000.
-  **maxevaluations**: The maximum number of iterations to use for the
   minimization. This value corresponds to the maxeval term for the
   LAMMPS minimize command. Default value is 1000000.
-  **maxatommotion**: The maximum distance that any atom can move during
   a minimization iteration. This value is in units length and
   corresponds to the dmax term for the LAMMPS min_modify command.
   Default value is ‘0.01 angstrom’.

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

Run Parameters
--------------

-  **strainrange**: The strain range to apply to the system to evaluate
   the elastic constants. Default value is ‘1e-6’
