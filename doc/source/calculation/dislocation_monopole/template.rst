dislocation_monopole Input Terms
================================

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

Elastic Constants
-----------------

Specifies the computed elastic constants for the interatomic potential
and crystal structure, relative to the loaded system’s orientation. If
the values are specified with the Voigt Cij terms and the system is in a
standard setting for a crystal type, then only the unique Cij values for
that crystal type are necessary. If isotropic values are used, only two
idependent parameters are necessary.

-  **elasticconstants_file**: The path to a record containing the
   elastic constants to use. If neither this or the individual Cij
   components (below) are given and load_style is ‘system_model’, this
   will be set to load_file.
-  **C11**: The C11 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C12**: The C12 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C13**: The C13 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C14**: The C14 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C15**: The C15 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C16**: The C16 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C22**: The C22 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C23**: The C23 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C24**: The C24 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C25**: The C25 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C26**: The C26 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C33**: The C33 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C34**: The C34 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C35**: The C35 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C36**: The C36 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C44**: The C44 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C45**: The C45 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C46**: The C46 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C55**: The C55 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C56**: The C56 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C66**: The C66 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C_M**: The isotropic P-wave modulus (units of pressure).
-  **C_lambda**: The isotropic Lame’s first parameter (units of
   pressure).
-  **C_mu**: The isotropic shear modulus (units of pressure).
-  **C_E**: The isotropic Young’s modulus (units of pressure).
-  **C_nu**: The isotropic Poisson’s ratio (unitless).
-  **C_K**: The isotropic bulk modulus (units of pressure).

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

Dislocation
-----------

Specifies the parameter set that defines a dislocation type and how to
orient it relative to the atomic system.

-  **dislocation_file**: The path to a dislocation record file that
   collects the parameters for a specific dislocation type.
-  **dislocation_slip_hkl**: The Miller (hkl) slip plane for the
   dislocation given as three space-delimited integers.
-  **dislocation_ξ_uvw**: The Miller [uvw] line vector direction for the
   dislocation given as three space-delimited integers. The angle
   between burgers and ξ_uvw determines the dislocation’s character.
-  **dislocation_burgers**: The Miller Burgers vector for the
   dislocation given as three space-delimited floats.
-  **dislocation_m**: The Cartesian vector of the final system that the
   dislocation solution’s m vector (in-plane, perpendicular to ξ) should
   align with. Given as three space-delimited numbers. Limited to
   beingparallel to one of the three Cartesian axes.
-  **dislocation_n**: The Cartesian vector of the final system that the
   dislocation solution’s n vector (slip plane normal) should align
   with. Given as three space-delimited numbers. Limited to
   beingparallel to one of the three Cartesian axes.
-  **dislocation_shift**: A rigid body shift to apply to the atoms in
   the system after it has been rotated to the correct orientation. This
   controls where the dislocation is placed relative to the atomic
   positions as the dislocation line is always inserted at coordinates
   (0,0) for the two Cartesian axes aligned with m and n. Specified as
   three floating point numbers.
-  **dislocation_shiftscale**: boolean indicating if the
   dislocation_shift value is a Cartesian vector (False, default) or if
   it is scaled relative to the rotated cell’s box parameters prior to
   applying sizemults.
-  **dislocation_shiftindex**: An integer that if given will result in a
   shift being automatically determined and used such that the
   dislocation’s slip plane will be positioned halfway between two
   atomic planes. Changing the integer value changes which set of planes
   the slip plane is positioned between. Note that shiftindex values
   only shift atoms in the slip plane normal direction and therefore may
   not be the ideal positions for some dislocation cores.
-  **sizemults**: Multiplication parameters to construct a supercell
   from the rotated system. Limited to three values for dislocation
   generation. Values must be even for the two box vectors not aligned
   with the dislocation line. The system will be replicated equally in
   the positive and negative directions for those two box vectors.
-  **amin**: Specifies a minimum width in length units that the
   resulting system’s a box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.
-  **bmin**: Specifies a minimum width in length units that the
   resulting system’s b box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.
-  **cmin**: Specifies a minimum width in length units that the
   resulting system’s c box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.

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

-  **annealtemperature**: The temperature at which to anneal the
   dislocation system If 0, then no MD anneal will be performed.
-  **annealsteps**: The number of MD steps to perform at the anneal
   temperature before running the energy/force minimization. Default
   value is 0 if annealtemperature=0, and 10,000 if annealtemperature >
   0.
-  **randomseed**: An int random number seed to use for generating
   initial velocities. A random int will be selected if not given.
-  **dislocation_boundaryshape**: ‘box’ or ‘cylinder’ specifying the
   resulting shape of the active region after defining the boundary
   atoms. For ‘box’, the boundary width is constant at the two
   non-periodic box edges. For ‘cylinder’, the active region is a
   cylinder centered around the dislocation line. Default value is
   ‘cylinder’.
-  **dislocation_boundarywidth**: The minimum thickness of the boundary
   region.
-  **dislocation_boundaryscale**: Boolean indicating if boundarywidth is
   taken as Cartesian (False) or scaled by the loaded unit cell’s a
   lattice parameter.
