Input script parameters
-----------------------

This is a list of the input parameter names recognized by the
calculation script.

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

Initial system configuration to load
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the information associated with loading an atomic
configuration.

-  **load_file**: the path to the initial configuration file being read
   in.

-  **load_style**: the style/format for the load_file. The style can be
   any file type supported by atomman.load()

-  **load_options**: a list of key-value pairs for the optional
   style-dependent arguments used by atomman.load().

-  **family**: specifies the configuration family to associate with the
   loaded file. This is typically a crystal structure/prototype
   identifier that helps with linking calculations on the same material
   together. If not given and the load_style is system_model, then the
   family will be taken from the file if included. Otherwise, the family
   will be taken as load_file stripped of path and extension.

-  **symbols**: a space-delimited list of the potential’s atom-model
   symbols to associate with the loaded system’s atom types. Required if
   load_file does not contain this information.

-  **box_parameters**: allows for the specification of new box
   parameters to scale the loaded configuration by. This is useful for
   running calculations based on prototype configurations that do not
   contain material-specific dimensions. Can be given either as a list
   of three or six numbers, with an optional unit of length at the end.
   If the unit of length is not given, the specified length_unit (below)
   will be used.

   -  a b c (unit): for orthogonal boxes.

   -  a b c alpha beta gamma (unit): for triclinic boxes. The angles are
      taken in degrees.

System manipulations
~~~~~~~~~~~~~~~~~~~~

Performs simple manipulations on the loaded initial system.

-  **a_uvw, b_uvw, c_uvw**: are crystallographic Miller vectors to
   rotate the system by such that the rotated system’s a, b, c box
   vectors correspond to the specified Miller vectors of the loaded
   configuration. Using crystallographic vectors for rotating ensures
   that if the initial configuration is periodic in all three
   directions, the resulting rotated configuration can be as well with
   no boundary incompatibilities. Default values are ‘1 0 0’, ‘0 1 0’,
   and ‘0 0 1’, respectively (i.e. no rotation).

-  **atomshift**: a vector positional shift to apply to all atoms. The
   shift is relative to the size of the system after rotating, but
   before sizemults have been applied. This allows for the same relative
   shift regardless of box_parameters and sizemults. Default value is
   ‘0.0 0.0 0.0’ (i.e. no shift).

-  **sizemults**: multiplication parameters for making a supercell of
   the loaded system. This may either be a list of three or six integer
   numbers. Default value is ‘10 10 10’.

   -  ma mb mc: multipliers for each box axis. Values can be positive or
      negative indicating the direction relative to the original box’s
      origin for shifting/multiplying the system.

   -  na pa nb pb nc pc: negative, positive multiplier pairs for each
      box axis. The n terms must be less than or equal to zero, and the
      p terms greater than or equal to zero. This allows for expanding
      the system in both directions relative to the original box’s
      origin.

Defect Parameters
~~~~~~~~~~~~~~~~~

Defines the defect system to construct and analyze.

-  **pointdefect_file**: the path to a point_defect record file that
   contains a set of input parameters associated with a specific point
   defect or set of point defects. In particular, the point_defect
   record contains values for the pointdefect_type, pointdefect_atype,
   pointdefect_pos, pointdefect_dumbbell_vect, and pointdefect_scale
   parameters. As such, those parameters cannot be specified separately
   if pointdefect_model is given.

-  **pointdefect_type**: indicates which type of point defect to
   generate.

   -  ‘v’ or ‘vacancy’: generate a vacancy.

   -  ‘i’ or ‘interstitial’: generate a position-based interstitial.

   -  ‘s’ or ‘substitutional’: generate a substitutional.

   -  ‘d’, ‘db’ or ‘dumbbell’: generate a dumbbell interstitial.

-  **pointdefect_atype**: indicates the integer atom type to assign to
   an interstitial, substitutional, or dumbbell interstitial atom.

-  **pointdefect_pos**: indicates the position where the point defect is
   to be placed. For the interstitial type, this cannot correspond to a
   current atom’s position. For the other styles, this must correspond
   to a current atom’s position.

-  **pointdefect_dumbbell_vect**: specifies the dumbbell vector to use
   for a dumbbell interstitial. The atom defined by pointdefect_pos is
   shifted by -pointdefect_dumbbell_vect, and the inserted interstitial
   atom is placed at pointdefect_pos + pointdefect_dumbbell_vect.

-  **pointdefect_scale**: Boolean indicating if pointdefect_pos and
   pointdefect_dumbbell_vect are taken as absolute Cartesian vectors, or
   taken as scaled values relative to the loaded system. Default value
   is False.

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

Run parameters
~~~~~~~~~~~~~~

Provides parameters specific to the calculation at hand.

-  **temperature**: temperature in Kelvin at which to run the MD
   integration scheme at. Default value is ‘0’.

-  **runsteps**: specifies how many timesteps to integrate the system.
   Default value is 200000.

-  **thermosteps**: specifies how often LAMMPS prints the system-wide
   thermo data. Default value is runsteps/1000, or 1 if runsteps is less
   than 1000.

-  **dumpsteps**: specifies how often LAMMPS saves the atomic
   configuration to a LAMMPS dump file. Default value is runsteps,
   meaning only the first and last states are saved.

-  **equilsteps**: specifies how many timesteps are ignored as
   equilibration time when computing the mean box parameters. Default
   value is 10000.

-  **randomseed**: provides a random number seed to generating the
   initial atomic velocities. Default value gives a random number as the
   seed.
