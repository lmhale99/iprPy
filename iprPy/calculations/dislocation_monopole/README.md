# dislocation_monopole

--------------------------------------------------------------------------------

**Lucas M. Hale**, 
[lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), 
*Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, 
[chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), 
*Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, 
[zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), 
*Materials Measurement Science Division, NIST*.

Version: 2017-04-14

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
--------------------------------------------------------------------------------

## Contents

- [Calculation description](#calc)

- [Calculation input parameter names](#calc-in)

- [Prepare description](#prepare)

- [Prepare input parameter names](#prepare-in)

--------------------------------------------------------------------------------

## <a name="calc"></a>Calculation description

The __dislocation_monopole__ calculation inserts a dislocation monopole into an 
atomic system using the anisotropic elasticity solution for a straight perfect 
dislocation, and relaxes the atomic configuration. The calculation follows the 
convention that the system is oriented with the dislocation line parallel to the 
Cartesian z-axis and positioned at x,y coordinates (0, 0), and the slip plane 
normal to the y-axis. The system is periodic along the box's c vector, and 
non-periodic in the other two box vector directions. The non-periodic bounds are
handled by defining a boundary region of atoms held fixed at the elasticity 
solution. The atoms within the active region of the system are relaxed using nvt
integration (if a non-zero temperature is specified), followed by an 
energy/force minimization (even if the temperature is zero).

The relaxed dislocation system and corresponding dislocation-free base systems 
are retained in the calculation's archived record. Various properties associated
with the dislocation's elasticity solution are recorded in the calculation's 
results record.

__Disclaimer #1__: The underlying algorithms should be general enough for any 
straight, perfect dislocation in any material with any crystal family. However, 
the current version with the dislocation line along the z-axis means that the c 
vector should also be parallel to the z-axis to retain the dislocation's 
periodicity. This can restrict which and how some dislocations in non-cubic 
materials can be represented. Additionally, a more generalized handling of 
vectors and rotations is needed before non-cubic systems will be fully 
supported.

__Disclaimer #2__: Performing the calculation at 0K is faster as it skips the 
nvt integration, but the resulting structure may not be fully relaxed. Also, 
after relaxation the dislocation's position may shift.

__Disclaimer #3__: The sizes of the system and boundary region should be 
selected to place the dislocation far from the boundary region to reduce the 
effect of the boundary region on the dislocation. Care needs to be taken in
selecting proper sizemults, atomshift and boundarywidth parameters. See their 
explanations below for more information.

--------------------------------------------------------------------------------

## <a name="calc-in"></a>Calculation input parameter names

This is a list of the input parameter names recognized by the calculation
script.

### Commands

Provides the external commands for running LAMMPS and MPI.

- __lammps_command__: the path to the executable for running LAMMPS on your
  system. Don't include command line options.

- __mpi_command__: the path to the MPI executable and any command line options
  to use for calling LAMMPS to run in parallel on your system. Default value is
  None (run LAMMPS as a serial process).

### Potential

Provides the information associated with an interatomic potential implemented
for LAMMPS.

- __potential_file__: the path to the LAMMPS-potential data model used by 
  atomman to generate the proper LAMMPS commands for an interatomic potential. 
 
- __potential_dir__: the path to the directory containing any potential 
  artifacts (eg. eam setfl files) that are used. If not given, then any required
  files are expected to be in the working directory where the calculation is 
  executed.

### System Load

Provides the information associated with loading an atomic configuration.

- __load__: the style and path to the initial configuration file being read in.
  The style can be any file type supported by 
  [atomman.load](https://github.com/usnistgov/atomman/blob/master/docs/reference/atomman.load.ipynb).
 
- __load_options__: a list of key-value pairs for the optional style-dependent 
  arguments used by 
  [atomman.load](https://github.com/usnistgov/atomman/blob/master/docs/reference/atomman.load.ipynb). 
 
- __symbols__: a space-delimited list of the potential's atom-model symbols to
  associate with the loaded system's atom types. Required if the configuration 
  load file does not contain this information. 
 
- __box_parameters__: box parameters to scale the loaded system to. Can be 
  given either as a list of three or six numbers. Either format can be appended
  with an extra term specifying the length unit for the box parameters. Optional
  for when you want to scale an initial loaded configuration. For this
  calculation, the box_parameters provide the initial guess for the equilibrium
  lattice constants.
    
    - a b c: allows for the definition of orthorhombic box parameters (length 
      units).
    
    - a b c alpha beta gamma: allows for the definition of triclinic box 
      parameters (in length units) and angles (in degrees).
    
### System Manipulations

Performs manipulations on the loaded system. 

- __x_axis, y_axis, z_axis__: transformation axes for rotating the system. Each
  vector is given by three space-delimited numbers. The vectors must be 
  orthogonal to each other. If the loaded system is cubic, these vectors are 
  taken as hkl crystallographic directions and the rotated system is transformed
  into an orthorhombic box with dimensions given by $a \sqrt{h^2+k^2+l^2}$ for 
  each axis. Default values are '1 0 0', '0 1 0', and '0 0 1', respectively.

- __atomshift__: a vector positional shift to apply to all atoms. The shift is 
  relative to the size of the system after rotating, but before sizemults have 
  been applied. This allows for the same relative shift regardless of 
  box_parameters and sizemults. For this calculation, the y-coordinate of the 
  shift should be such that the mathematical y=0 slip plane does not correspond
  to an atomic plane within the system. Default value is '0.0 0.1 0.0'.

- __sizemults__: multiplication parameters for making a supercell of the loaded
  system. This may either be a list of three or six integer numbers. The six 
  number version should be used for this calculation, ideally with na = -pa, and
  nb = -pb to place the dislocation at the exact center of the system. Default 
  value is '-10 10 -10 10 0 3'.

    - ma mb mc: multipliers for each box axis. Values can be positive or 
      negative indicating the direction relative to the original box's origin 
      for shifting/multiplying the system.  
    
    - na pa nb pb nc pc: negative, positive multiplier pairs for each box axis.
      The n terms must be less than or equal to zero, and the p terms greater
      than or equal to zero. This allows for expanding the system in both
      directions relative to the original box's origin.
    
### Units

Specifies the units for various physical quantities to use when saving values to
the results record file. Also used as the default units for parameters in this
input parameter file.

- __length_unit__: defines the unit of length for results, and input parameters 
  if not directly specified. Default value is 'angstrom'.

- __energy_unit__: defines the unit of energy for results, and input parameters 
  if not directly specified. Default value is 'eV'.

- __pressure_unit__: defines the unit of pressure for results, and input 
  parameters if not directly specified. Default value is 'GPa'.

- __force_unit__: defines the unit of pressure for results, and input parameters
  if not directly specified. Default value is 'eV/angstrom'.

### Defect Parameters

Defines the defect system to construct and analyze.

- __dislocation_model__: the path to a dislocation-monopole record file that 
  contains a set of input parameters associated with a specific dislocation 
  monopole. In particular, the dislocation-monopole record contains values for
  the x_axis, y_axis, z_axis, atomshift, and burgers parameters. As such, those 
  parameters cannot be specified separately if dislocation_model is given.
  
- __burgers__: the Burgers vector of the dislocation. This is taken as the hkl
  crystallographic vector relative to the loaded system. 

-__boundarywidth__: specifies the minimum thickness of the fixed-atom xy 
  boundary region. The value is in scaled units relative to the loaded system's 
  a vector magnitude, i.e. a value of 3 specifies a thickness of 3a. This value
  should be larger than the interatomic potential's cutoff distance so that all
  atoms not in the boundary region do not see a free surface. Default value is 
  3.0.

- __boundaryshape__: defines the shape of the fixed-atom boundary region. The 
  names of the options correspond to the xy cross-sectional shape of the 
  non-boundary region of atoms. Default value is 'circle'.
    
    - 'circle': the active region has a circular cross-section with a radius 
      defined such that the width of the boundary region is always at least 
      boundarywidth thick. The dislocation is initially placed at the center of
      the resulting active cylinder, meaning that it is equidistant from the 
      boundary region in all directions.  
    
    - 'rect': the active region has a rectangular cross-section, and the 
      boundary region is exactly boundarywidth thick all around. This option 
      maximizes the number of atoms within the system that are allowed to relax.
  
### Elastic Constants Parameters

Defines the elastic constants associated with the loaded system to use when 
generating the dislocation.

- __elasticconstants_model__: the path to a record file containing an 
  elastic-constants sub-element. If specified, all elastic constants will be 
  read in from the file providing values for all Cij parameters. As such, those
  parameters cannot be specified separately if elasticconstants_model is given.
  If neither elasticconstants_model and Cij terms are specified, then the 
  elasticconstants_model is taken as the path to the loaded system's record
  file.
  
- __Cij (C11, C12, ...C66)__: the individual components of the elastic constants
  tensor associated with the loaded system (in pressure units).
  
### Run Parameters

Provides parameters specific to the calculation at hand.

- __annealtemperature__: temperature at which to anneal the system for 10000 nvt
  steps prior to the energy/force minimization. Usually a small temperature
  around 50-100 K is enough. If annealtemperature is zero, then only the
  energy/force minimization is performed. Default value is 0.0.

- __energytolerance__: specifies the energy tolerance to use for the 
  minimization. This value is unitless and corresponds to the etol term for the
  [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default
  value is 0.

- __forcetolerance__: specifies the force tolerance to use for the minimization.
  This value is in force units and corresponds to the ftol term for the [LAMMPS 
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value 
  is '1.0e-6 eV/angstrom'.

- __maxiterations__: specifies the maximum number of iterations to use for the 
  minimization. This value corresponds to the maxiter term for the [LAMMPS
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value
  is 100000.

- __maxevaluations__: specifies the maximum number of iterations to use for the
  minimization. This value corresponds to the maxeval term for the [LAMMPS
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value
  is 100000.
 
- __maxatommotion__: specifies the maximum distance that any atom can move
  during a minimization iteration. This value is in units length and corresponds
  to the dmax term for the 
  [LAMMPS min_modify command.](http://lammps.sandia.gov/doc/min_modify.html) 
  Default value is '0.01 angstrom'.

--------------------------------------------------------------------------------

## <a name="prepare"></a>Prepare description

Prepare for __dislocation_monopole__ creates defect calculations based on the 
information provided by dislocation-monopole records and parent 
calculation-system-relax records. The default behavior is to retrieve all records 
of these types from a database, but limiters can be defined in the input script 
that restrict which are included. Alternatively, a list of pre-selected 
calculation-system-relax records from the database can be passed in if the 
calculation's prepare method is called directly. 

A calculation is prepared for every pair of the selected dislocation-monopole and 
calculation-system-relax records that are associated with the same crystal 
family (prototype). For each prepared calculation, a corresponding 
calculation-dislocation-monopole record is added to the database.

__Disclaimer #1__: While multiple dislocation types can be prepared 
simultaneously, it may be preferable to do one at a time. Optimally, the x and y
dimensions of the system should be comparable. Since each dislocation model has 
a unique orientation, the sizemults to make the two dimensions comparable will 
vary.

--------------------------------------------------------------------------------

## <a name="prepare-in"></a>Prepare input parameter names

This is a list of the input parameter names recognized by the prepare script.

### Database and run_directory

These terms define the access parameters for the database to get/save records,
and the location of the run_directory where the prepared calculation folders are
to be added. These parameters are necessary when running a calculation's prepare 
script, but are not needed when preparing from the iprPy inline command or from 
the calculation's prepare method.

- __database__: database style and host name.

- __database_\*__: any additional access parameters required by the database.

- __run_directory__: path to the directory where copies of the calculation are
  to be prepared.

### Commands

Provides the external commands for running LAMMPS and MPI.

- __lammps_command__: the path to the executable for running LAMMPS on your
  system. Don't include command line options.

- __mpi_command__: the path to the MPI executable and any command line options
  to use for calling LAMMPS to run in parallel on your system. Default value is
  None (run LAMMPS as a serial process).

### Parent record limiters

Limiters for which parent records to create calculations based on. If none of
these terms are given, then calculations are prepared for every parent record
stored in the database.

- __potential_name__: [multiple values allowed] only parent records associated
  with the named potentials will be included. Default value places no
  restrictions.

- __symbol_name__: [multiple values allowed] only parent records associated
  with the named element symbols will be included. Default value places no
  restrictions.

- __prototype_name__: [multiple values allowed] only parent records associated
  with the named crystal prototypes will be included. Default value places no
  restrictions.

- __dislocation_name__: [multiple values allowed] only dislocation-monopole 
  records associated with the named surface will be included. Default value 
  places no restrictions.
  
### System Manipulations

- __sizemults__: multiplication parameters for making a supercell of the loaded
  system. This may either be a list of three or six integer numbers. The six 
  number version should be used for this calculation, ideally with na = -pa, and
  nb = -pb to place the dislocation at the exact center of the system. Default 
  value is '-10 10 -10 10 0 3'.

    - ma mb mc: multipliers for each box axis. Values can be positive or 
      negative indicating the direction relative to the original box's origin 
      for shifting/multiplying the system.  
    
    - na pa nb pb nc pc: negative, positive multiplier pairs for each box axis.
      The n terms must be less than or equal to zero, and the p terms greater
      than or equal to zero. This allows for expanding the system in both
      directions relative to the original box's origin.
      
### Units

Specifies the units for various physical quantities to use when saving values to
the results record file. Also used as the default units for parameters in this
input parameter file.

- __length_unit__: defines the unit of length for results, and input parameters 
  if not directly specified. Default value is 'angstrom'.

- __energy_unit__: defines the unit of energy for results, and input parameters 
  if not directly specified. Default value is 'eV'.

- __pressure_unit__: defines the unit of pressure for results, and input 
  parameters if not directly specified. Default value is 'GPa'.

- __force_unit__: defines the unit of pressure for results, and input parameters
  if not directly specified. Default value is 'eV/angstrom'.

### Defect Parameters

Defines the defect system to construct and analyze.

-__boundarywidth__: specifies the minimum thickness of the fixed-atom xy 
  boundary region. The value is in scaled units relative to the loaded system's 
  a vector magnitude, i.e. a value of 3 specifies a thickness of 3a. This value
  should be larger than the interatomic potential's cutoff distance so that all
  atoms not in the boundary region do not see a free surface. Default value is 
  3.0.

- __boundaryshape__: defines the shape of the fixed-atom boundary region. The 
  names of the options correspond to the xy cross-sectional shape of the 
  non-boundary region of atoms. Default value is 'circle'.
    
    - 'circle': the active region has a circular cross-section with a radius 
      defined such that the width of the boundary region is always at least 
      boundarywidth thick. The dislocation is initially placed at the center of
      the resulting active cylinder, meaning that it is equidistant from the 
      boundary region in all directions.  
    
    - 'rect': the active region has a rectangular cross-section, and the 
      boundary region is exactly boundarywidth thick all around. This option 
      maximizes the number of atoms within the system that are allowed to relax.
  
### Run Parameters

Provides parameters specific to the calculation at hand.

- __annealtemperature__: temperature at which to anneal the system for 10000 nvt
  steps prior to the energy/force minimization. Usually a small temperature
  around 50-100 K is enough. If annealtemperature is zero, then only the
  energy/force minimization is performed. Default value is 0.0.

- __energytolerance__: specifies the energy tolerance to use for the 
  minimization. This value is unitless and corresponds to the etol term for the
  [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default
  value is 0.

- __forcetolerance__: specifies the force tolerance to use for the minimization.
  This value is in force units and corresponds to the ftol term for the [LAMMPS 
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value 
  is '1.0e-6 eV/angstrom'.

- __maxiterations__: specifies the maximum number of iterations to use for the 
  minimization. This value corresponds to the maxiter term for the [LAMMPS
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value
  is 100000.

- __maxevaluations__: specifies the maximum number of iterations to use for the
  minimization. This value corresponds to the maxeval term for the [LAMMPS
  minimize command.](http://lammps.sandia.gov/doc/minimize.html) Default value
  is 100000.
 
- __maxatommotion__: specifies the maximum distance that any atom can move
  during a minimization iteration. This value is in units length and corresponds
  to the dmax term for the 
  [LAMMPS min_modify command.](http://lammps.sandia.gov/doc/min_modify.html) 
  Default value is '0.01 angstrom'.