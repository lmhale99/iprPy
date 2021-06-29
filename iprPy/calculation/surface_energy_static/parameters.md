## Input script parameters

This is a list of the input parameter names recognized by calc_surface_energy_static.py.

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

### Free Surface Defect Parameters

Defines a free surface defect system to construct and analyze.

- __surface_file__: the path to a free-surface record file that contains a set of input parameters associated with a particular free surface.
- __surface_hkl__ three integers specifying the Miller (hkl) plane which the surface will be created for.
- __surface_cellsetting__ indicates the conventional cell setting for the crystal to use for specifying *surface_hkl* if the given unit cell is primitive.  Values are 'p', 'c', 'i', 'a', 'b' and 'c'.  Default value is 'p', i.e. the hkl values will be taken as directly related to the loaded unit cell.
- __surface_cutboxvector__: specifies which of the three box vectors ('a', 'b', or 'c') is to be made non-periodic to create the free surface.  Default value is 'c'.
- __surface_shiftindex__: integer indicating which rigid body shift to apply to the system before making the cut.  This effectively controls the atomic termination planes.
- __sizemults__: three integers specifying the box size multiplications to use.
- __surface_minwidth__: floating point number stating the minimum width along the cutboxvector direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __surface_even__: boolean indicating if the number of replicas in the cutboxvector direction must be even.  Default value is False.

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

