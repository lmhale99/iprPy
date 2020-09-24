## Input script parameters

This is a list of the input parameter names recognized by calc_dislocation_monopole.py.

### Global metadata parameters

- __branch__: assigns a group/branch descriptor to the calculation which can help with parsing results later.  Default value is 'main'.

### Command lines for LAMMPS and MPI

Provides the external commands for running LAMMPS and MPI.

- __lammps_command__: the path to the executable for running LAMMPS on your system.  Don't include command line options.
- __mpi_command__: the path to the MPI executable and any command line options to use for calling LAMMPS to run in parallel on your system. Default value is None (run LAMMPS as a serial process).

### Potential definition and directory containing associated files

Provides the information associated with an interatomic potential implemented for LAMMPS.

- __potential_file__: the path to the potential_LAMMPS data model used by atomman to generate the proper LAMMPS commands for an interatomic potential.
- __potential_dir__: the path to the directory containing any potential artifacts (eg. eam.alloy setfl files) that are used. If not given, then any required files are expected to be in the working directory where the calculation is executed.

### Initial system configuration to load

Provides the information associated with loading an atomic configuration.

- __load_file__: the path to the initial configuration file being read in.
- __load_style__: the style/format for the load_file.  The style can be any file type supported by atomman.load()
- __load_options__: a list of key-value pairs for the optional style-dependent arguments used by atomman.load().
- __family__: specifies the configuration family to associate with the loaded file.  This is typically a crystal structure/prototype identifier that helps with linking calculations on the same material together.  If not given and the load_style is system_model, then the family will be taken from the file if included.  Otherwise, the family will be taken as load_file stripped of path and extension.
- __symbols__: a space-delimited list of the potential's atom-model symbols to associate with the loaded system's atom types.  Required if load_file does not contain this information.
- __box_parameters__: *Note that this parameter has no influence on this calculation.*  allows for the specification of new box parameters to scale the loaded configuration by.  This is useful for running calculations based on prototype configurations that do not contain material-specific dimensions.  Can be given either as a list of three or six numbers, with an optional unit of length at the end.  If the unit of length is not given, the specified length_unit (below) will be used.
  - a b c (unit): for orthogonal boxes.
  - a b c alpha beta gamma (unit): for triclinic boxes.  The angles are taken in degrees.

### Elastic constants parameters

Specifies the computed elastic constants for the interatomic potential and crystal structure, relative to the loaded system's orientation.

- __elasticconstants_file__: the path to a record containing the elastic constants to use.  If neither this or the individual Cij components (below) are given and *load_style* is 'system_model', this will be set to *load_file*.
- __C11, C12, C13, C14, C15, C16, C22, C23, C24, C25, C26, C33, C34, C35, C36, C44, C45, C46, C55, C56, C66__: the individual elastic constants components in units of pressure.  If the loaded system's orientation is the standard setting for the crystal type, then missing values will automatically be filled in. Example: if the loaded system is a cubic prototype, then only C11, C12 and C44 need be specified.
- Isotropic moduli: the elastic constants for an isotropic material can be defined using any two of the following
  - __C_M__: P-wave modulus (units of pressure).  
  - __C_lambda__: Lame's first parameter (units of pressure).
  - __C_mu__: shear modulus (units of pressure).
  - __C_E__: Young's modulus (units of pressure).
  - __C_nu__: Poisson's ratio (unitless).
  - __C_K__: bulk modulus (units of pressure).

### Dislocation defect parameters

Defines a unique dislocation type and orientation

- __dislocation_file__: the path to a dislocation_monopole record file that contains a set of input parameters associated with a specific dislocation.
- __dislocation_slip_hkl__: three integers specifying the Miller (hkl) slip plane for the dislocation.
- __dislocation_Î¾_uvw__: three integers specifying the Miller \[uvw\] line vector direction for the dislocation.  The angle between burgers and Î¾_uvw determines the dislocation's character
- __dislocation_burgers__: three floating point numbers specifying the crystallographic Miller Burgers vector for the dislocation.
- __dislocation_m__ three floats for the Cartesian vector of the final system that the dislocation solution's m vector (in-plane, perpendicular to Î¾) should align with.  Limited to being parallel to one of the three Cartesian axes.  
- __dislocation_n__ three floats for the Cartesian vector of the final system that the dislocation solution's n vector (slip plane normal) should align with.  Limited to being parallel to one of the three Cartesian axes.
- __dislocation_shift__: three floating point numbers specifying a rigid body shift to apply to the atoms in the system. This controls how the atomic positions align with the ideal position of the dislocation core, which is at coordinates (0,0) for the two Cartesian axes aligned with m and n.
- __dislocation_shiftscale__: boolean indicating if the *dislocation_shift* value should be absolute (False) or scaled relative to the rotated cell used to construct the system.
- __dislocation_shiftindex__: integer alternate to specifying shift values, the shiftindex allows for one of the identified suggested shift values to be used that will position the slip plane halfway between two planes of atoms.  Note that shiftindex values only shift atoms in the slip plane normal direction and may not be the ideal positions for some dislocation cores.
- __sizemults__: three integers specifying the box size multiplications to use.
- __amin__: floating point number stating the minimum width along the a direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __bmin__: floating point number stating the minimum width along the b direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __cmin__: floating point number stating the minimum width along the c direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.

### Units for input/output values

Specifies the units for various physical quantities to use when saving values to the results record file. Also used as the default units for parameters in this input parameter file.

- __length_unit__: defines the unit of length for results, and input parameters if not directly specified.  Default value is 'angstrom'.
- __energy_unit__: defines the unit of energy for results, and input parameters if not directly specified.  Default value is 'eV'.
- __pressure_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'GPa'.
- __force_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'eV/angstrom'.

### LAMMPS minimization parameters

Specifies the run parameters associated with an energy/force minimization in LAMMPS.

- __energytolerance__: specifies the energy tolerance to use for the minimization.  This value is unitless and corresponds to the etol term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 0.
- __forcetolerance__: specifies the force tolerance to use for the minimization.  This value is in force units and corresponds to the ftol term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is '1.0e-10 eV/angstrom'.
- __maxiterations__: specifies the maximum number of iterations to use for the minimization. This value corresponds to the maxiter term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 1000.
- __maxevaluations__: specifies the maximum number of iterations to use for the minimization. This value corresponds to the maxeval term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 10000.
- __maxatommotion__: specifies the maximum distance that any atom can move during a minimization iteration. This value is in units length and corresponds to the dmax term for the [LAMMPS min_modify command.](http://lammps.sandia.gov/doc/min_modify.html)  Default value is '0.01 angstrom'.

### Run Parameters

Provides parameters specific to the calculation at hand.

- __annealtemperature__: specifies the temperature at which to anneal the dislocation system.
- __annealsteps__: specifies how many MD steps to perform at the anneal temperature before running the energy/force minimization.  Default value is 0 if annealtemperature=0, and 10,000 if annealtemperature > 0.
- __randomseed__: provides a random number seed to generating the initial atomic velocities.  Default value gives a random number as the seed.
- __dislocation_boundaryshape__: 'box' or 'cylinder' specifying the resulting shape of the active region after defining the boundary atoms.  For 'box', the boundary width is constant at the two non-periodic box edges.  For 'cylinder', the active region is a cylinder centered around the dislocation line.  Default value is 'cylinder'.
- __dislocation_boundarywidth__: floating point number specifying the minimum thickness of the boundary region.
- __dislocation_boundaryscale__: boolean indicating if the boundary width is taken as absolute (False) or should be scaled by the loaded unit cell's a lattice parameter.
