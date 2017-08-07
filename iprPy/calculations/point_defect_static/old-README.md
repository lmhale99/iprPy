# point_defect_static

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

Version: 2017-04-17

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
--------------------------------------------------------------------------------

## Contents

- [Calculation description](#calc)

- [Calculation input parameter names](#calc-in)

- [Prepare description](#prepare)

- [Prepare input parameter names](#prepare-in)

--------------------------------------------------------------------------------

## <a name="calc"></a>Calculation description

The __point_defect_static__ calculation computes the formation energy of a point
defect. It first generates a perfect crystal system, and computes the cohesive 
energy, $E_coh$, of the system. A point defect, or a collection of point defects
are then inserted using the atomman.defect.point method. After insertion, the 
system is relaxed using an energy/force minimization. The formation energy of 
the defect is obtained as $E_ptd - E_coh * natoms$, where $E_ptd$ is the total 
potential energy of the system containing the point defect, and natoms is the 
number of atoms in the defect system.

The defect-containing system is then analyzed using a few simple metrics to 
determine whether or not the point defect configuration has relaxed to a lower
energy configuration. For all types of point defects, the centrosummation 
metric adds up the vector positions of atoms relative to the defect's position 
for all atoms within a specified cutoff. For interstitial and substitutional 
atoms, the position_shift metric is the vector difference between the defect's 
initial and final positions. For dumbbell interstitials, the db_vect_shift 
metric identifies the unit vector for the dumbbell, and measures the change in
the unit dumbbell vector between the initial and final positions. If any of the
metrics have values not close to (0,0,0), then there was likely an atomic 
configuration relaxation.

The final defect system and the associated perfect base system are retained in 
the calculation's archive. The calculation's record reports the base system's 
cohesive energy, the point defect's formation energy, and the values of any of 
the reconfiguration metrics used.

__Disclaimer #1__: Point defect formation values are sensitive to the size of 
the system. Larger systems minimize the interaction between the defects, and the
affect that the defects have on the system's pressure. Infinite system formation
energies can be estimated by measuring the formation energy for multiple system 
sizes, and extrapolating to 1/natoms = 0.

__Disclaimer #2__: Because only a static relaxation is performed, the final 
configuration might not be the true stable configuration. Additionally, the 
stable configuration may not correspond to any of the standard configurations 
characterized by the point-defect records in the iprPy/library. Running multiple
configurations increases the likelihood of finding the true stable state, but it
does not guarantee it. 

__Disclaimer #3__: The reconfiguration metrics should be considered as 
guidelines, not as absolute. Because most standard sites for point defects are 
positions of high-symmetry, they will likely work well for most simple cases. 

__Disclaimer #4__: The current version assumes that the initial defect-free base 
system is an elemental crystal structure. The formation energy expression will 
have to updated to handle multi-component crystals. 

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
  value is '5 5 5'.

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

- __pointdefect_model__: the path to a point-defect record file that contains a set of input parameters associated with a specific point defect or set of point defects. In particular, the point-defect record contains values for the pointdefect_type, pointdefect_atype, pointdefect_pos, pointdefect_dumbbell_vect, and pointdefect_scale parameters. As such, those parameters cannot be specified separately if pointdefect_model is given.
  
- __pointdefect_type__: indicates which type of point defect to generate. 

    - 'v' or 'vacancy': generate a vacancy.

    - 'i' or 'interstitial': generate a position-based interstitial.
    
    - 's' or 'substitutional': generate a substitutional.
    
    - 'd', 'db' or 'dumbbell': generate a dumbbell interstitial.
    
- __pointdefect_atype__: indicates the integer atom type to assign to an interstitial, substitutional, or dumbbell interstitial atom. 

- __pointdefect_pos__: indicates the position where the point defect is to be placed. For the interstitial type, this cannot correspond to a current atom's position. For the other styles, this must correspond to a current atom's position.

- __pointdefect_dumbbell_vect__: specifies the dumbbell vector to use for a dumbbell interstitial. The atom defined by pointdefect_pos is shifted by -pointdefect_dumbbell_vect, and the inserted interstitial atom is placed at pointdefect_pos + pointdefect_dumbbell_vect. 

- __pointdefect_scale__: Boolean indicating if pointdefect_pos and pointdefect_dumbbell_vect are taken as absolute Cartesian vectors, or taken as scaled values relative to the loaded system. Default value is False.
  
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

--------------------------------------------------------------------------------

## <a name="prepare"></a>Prepare description

Prepare for __point_defect_static__ creates defect calculations based on the 
information provided by point-defect records and parent calculation-system-relax 
records. The default behavior is to retrieve all records of these types from a 
database, but limiters can be defined in the input script that restrict which 
are included. Alternatively, a list of pre-selected calculation-system-relax 
records from the database can be passed in if the calculation's prepare method 
is called directly. 

A calculation is prepared for every pair of the selected point-defect and 
calculation-system-relax records that are associated with the same crystal 
family (prototype). The script also supports looping over multiple sizemults 
values. For each prepared calculation, a corresponding 
calculation-point-defect-formation record is added to the database.

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

- __pointdefect_name__: [multiple values allowed] only point-defect records 
  associated with the named surface will be included. Default value places no 
  restrictions.
  
### System Manipulations

- __sizemults__: [multiple values allowed] multiplication parameters for making
  a supercell of the loaded system. This may either be a list of three or six 
  integer numbers. Default value is '5 5 5'.

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