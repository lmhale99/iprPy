relax_liquid Input Terms
========================

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

-  **temperature**: The target temperature to relax to. Required.
-  **pressure**: The target hydrostatic pressure to relax to. Default
   value is 0.0 GPa
-  **temperature_melt**: The elevated temperature to first use to
   hopefully melt the initial configuration.
-  **rdfcutoff**: The cutoff distance to use for the RDF cutoff. If not
   given then will use 4 \* r0, where r0 is the shortest atomic distance
   found in the given system configuration.
-  **meltsteps**: The number of npt integration steps to perform during
   the melting stage at the melt temperature to create an amorphous
   liquid structure. Default value is 50000.
-  **coolsteps**: The number of npt integration steps to perform during
   the cooling stage where the temperature is reduced from the melt
   temperature to the target temperature. Default value is 10000.
-  **equilvolumesteps**: The number of npt integration steps to perform
   during the volume equilibration stage where the system is held at the
   target temperature and pressure to obtain an estimate for the relaxed
   volume. Default value is 50000.
-  **equilvolumesamples**: The number of thermo samples from the end of
   the volume equilibration stage to use in computing the average
   volume. Cannot be larger than equilvolumesteps / 100. It is
   recommended to set smaller than the max to allow for some convergence
   time. Default value is 300.
-  **equilenergysteps**: The number of nvt integration steps to perform
   during the energy equilibration stage where the system is held at the
   target temperature to obtain an estimate for the total energy.
   Default value is 10000.
-  **equilenergysamples**: The number of thermo samples from the end of
   the energy equilibrium stage to use in computing the target total
   energy. Cannot be larger than equilenergysteps / 100. Default value
   is 100.
-  **equilenergystyle**: Indicates which scheme to use for computing the
   target total energy. Allowed values are ‘pe’ or ‘te’. For ‘te’, the
   average total energy from the equilenergysamples is used as the
   target energy. For ‘pe’, the average potential energy plus 3/2 N kB T
   is used as the target energy. Default value is ‘pe’.
-  **runsteps**: The number of nve integration steps to perform on the
   system to obtain measurements of MSD and RDF of the liquid. Default
   value is 50000.
-  **dumpsteps**: Dump files will be saved every this many steps during
   the runsteps simulation. Default is None, which sets dumpsteps equal
   to the sum of all other steps values so only the final configuration
   is saved.
-  **restartsteps**: Restart files will be saved every this many steps.
   Default is None which sets restartsteps equal to the sum of all other
   steps values so only the final configuration is saved.
-  **randomseed**: Random number seed used by LAMMPS in creating
   velocities and with the Langevin thermostat. Default is None which
   will select a random int between 1 and 900000000.
