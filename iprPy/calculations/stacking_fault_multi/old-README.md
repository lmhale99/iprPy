# stacking_fault_multi

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

Version: 2017-03-31

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
--------------------------------------------------------------------------------

## Contents

- [Calculation description](#calc)

- [Calculation input parameter names](#calc-in)

- [Prepare description](#prepare)

- [Prepare input parameter names](#prepare-in)

--------------------------------------------------------------------------------

## <a name="calc"></a>Calculation description

The __stacking_fault_multi__ calculation evaluates the data points for the 2D generalized stacking fault map associated with a given crystallographic plane. This script computes the generalized stacking fault for a regular grid of data points along the glide plane. This is in contrast to the alternate stacking_fault calculation, which only computes the generalized stacking fault for one planar shift position. 

A perfect crystal system is constructed in which two of the system's box dimensions are periodic and the third is non-periodic. A mathematical fault plane is defined in the middle of the system parallel to the free surface plane created by the non-periodic boundary. All atoms on one side of the fault plane are then shifted by a specified amount, and the atoms in the system are allowed to relax normal to the plane. The generalized stacking fault energy is then computed as the potential energy difference between the system before and after the shift is applied divided by the area of the stacking fault plane. Additionally, the relaxation normal to the glide plane is characterized by finding the change in the centers of mass of the shifted and unshifted regions perpendicular to the glide plane. 

__Note__: To ensure that the shift is properly handled across the periodic directions, the system design is limited such that the free surface planes and the fault plane must be parallel to each other, as well as perpendicular to one of the principal Cartesian axes. In terms of the system's box vectors, only one box vector is allowed to have a component perpendicular to the fault plane. For example, if the fault plane is perpendicular to the Cartesian z-axis, then the system's a and b vectors must not have a component in the z-direction. As for the box's a vector in this example, it can have components along the x- and y-directions. 

__Disclaimer #1__: As only the points along the grid are explored and relaxations parallel to the slip plane are not allowed, the reported maximums and minimums are not fully refined. If you want specific stacking fault values, then either use many grid points, or make certain that the grid points directly correspond to any stacking fault positions of interest.

__Disclaimer #2__: The stacking_fault_multi calculation is more efficient both in terms of computation and data storage than the stacking_fault calculation in evaluating an array of points. However, the single point stacking_fault calculation may be preferable in certain situations, such as for irregular grids or in the case where it is impractical to explore a full grid all at once.


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
  box_parameters and sizemults. Default value is '0.0 0.0 0.0'.

- __sizemults__: multiplication parameters for making a supercell of the loaded
  system. This may either be a list of three or six integer numbers. Default 
  value is '3 3 3'.

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

- __stackingfault_numshifts1, stackingfault_numshifts2__: specifies the number of shift steps to divide the stackingfault_shiftvector directions up into. This includes the two endpoints, so it should always be one greater than 1/stepsize; a numshift value of 3 will measure at 0, shiftvector/2, and shiftvector. A value of 1 allows for the calculation of a 1D path along the other shiftvector to be calculated. Default value is 11 for both.

- __stackingfault_model__: the path to a stacking-fault record file that contains a set of input parameters associated with a specific generalized stacking fault plane. In particular, the stacking-fault record contains values for the x_axis, y_axis, z_axis, atomshift, stackingfault_planeaxis, stackingfault_planepos, stackingfault_shiftvector1, and stackingfault_shiftvector2 parameters. As such, those parameters cannot be specified separately if surface_model is given.
  
- __stackingfault_planeaxis__: indicates which Cartesian axis the fault plane and the free surface planes are made perpendicular to. Allowed values are 'x', 'y', and 'z'. See the [Calculation description](#calc) and the Note there for more details on this meaning and limitations of the system design. Default value is 'z'.
  
- __stackingfault_planepos__: specifies a fractional coordinate from 0 to 1 indicating where along the planeaxis direction in the crystal to position the fault plane. This is defined relative to the system after axes rotations have been applied, but before sizemults are used. This makes the planepos unique to a crystal prototype and orientation, and independent of lattice constants and sizemults. When sizemults is supplied, the fault plane is positioned within a replica near the center of the final system. If an odd sizemult is used for the planeaxis direction, then the fault plane is positioned at planepos within the middle replica. If an even sizemult is used for the planeaxis direction, then the fault plane is positioned at planepos within the replica on the positive side of the center of the system.

- __stackingfault_shiftvector1, stackingfault_shiftvector2__: defines one of the two directions of shifting associated with the 2D generalized stacking fault. This is taken as a crystallographic vector relative to the box vectors of the initial load configuration file. This is done so that these values have crystallographic meaning instead of just numerical meaning. Both vectors should be within the fault plane. Ideally, they should be set such that applying a full shiftvector shifts the system from one perfect periodic configuration to the next. 

The stacking fault parameters are perhaps easiest to understand with an example. The (111) fault plane for an fcc crystal can be explored with the following parameters:
   
        x_axis                      1 -1  0 
        y_axis                      1  1 -2 
        z_axis                      1  1  1 
        atomshift                   0.01 0.01 0.01 
        stackingfault_planeaxis     z 
        stackingfault_planepos      0.5 
        stackingfault_shiftvector1  0.5 -0.5  0.0 
        stackingfault_shiftvector2  0.5  0.5 -1.0

In particular, note that z_axis is [111], the cut is perpendicular to z, stackingfault_shiftvector1 is 1/2 x_axis (i.e. a/2[1 -1 0]), and stackingfault_shiftvector2 is 1/2 y_axis (i.e. a/2[1 1 -2]).

### Run Parameters

Provides parameters specific to the calculation at hand.

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
  
- __keepatomfiles__: boolean indicating if the atomic configuration files used and generated by the LAMMPS simulations are kept or deleted. While the atom files are useful for analyzing issues, they typically are not that important for this calculation and keeping them can quickly occupy large amounts of data storage. Default value is 'true' meaning the files are not deleted.

--------------------------------------------------------------------------------

## <a name="prepare"></a>Prepare description

Prepare for __stacking_fault_multi__ creates defect calculations based on the 
information provided by stacking-fault records and parent calculation-system-relax 
records. The default behavior is to retrieve all records of these types from a 
database, but limiters can be defined in the input script that restrict which 
are included. Alternatively, a list of pre-selected calculation-system-relax 
records from the database can be passed in if the calculation's prepare method 
is called directly. 

A calculation is prepared for every pair of the selected stacking-fault and 
calculation-system-relax records that are associated with the same crystal 
family (prototype). For each prepared calculation, a corresponding 
calculation-surface-energy record is added to the database.

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

- __stackingfault_name__: [multiple values allowed] only the stacking-fault 
  records with matching names will be included. Default value places no 
  restrictions.
  
### System Manipulations

- __sizemults__: multiplication parameters for making a supercell of the loaded
  system. This may either be a list of three or six integer numbers. Default 
  value is '3 3 3'.

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

### Run Parameters

Provides parameters specific to the calculation at hand.

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
  
- __keepatomfiles__: boolean indicating if the atomic configuration files used and generated by the LAMMPS simulations are kept or deleted. While the atom files are useful for analyzing issues, they typically are not that important for this calculation and keeping them can quickly occupy large amounts of data storage. Default value is 'true' meaning the files are not deleted.