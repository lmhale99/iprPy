# surface_energy

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

The __surface_energy__ calculation evaluates the formation energy for a free 
surface. An initially perfect bulk system with all three boundary conditions 
periodic is constructed and the system's potential energy is computed. One of 
the boundary conditions is then made non-periodic, effectively cutting the 
system and creating two free surfaces. The sliced system is then relaxed with an
energy/force minimization, and the total potential energy computed. The free 
surface formation energy is then computed as the change in energy of the system 
due to introducing the cut divided by the total surface area formed.

__Disclaimer #1__: Other atomic configurations at the free surface for certain 
planar cuts may have lower energies. The atomic relaxation will find a local 
minimum, which may not be the global minimum. Additionally, the material cut is 
planar perfect and therefore does not explore the effects of atomic roughness.

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

- __surface_model__: the path to a free-surface record file that contains a set 
  of input parameters associated with a particular free surface. In particular, 
  the free-surface record contains values for the x_axis, y_axis, z_axis, 
  atomshift, and surface_cutboxvector parameters. As such, those parameters 
  cannot be specified separately if surface_model is given.
  
- __surface_cutboxvector__: indicates along which box vector of the system the 
  planar cut is made, i.e. which box direction is made non-periodic. Allowed 
  values are 'a', 'b', and 'c' corresponding to making the first, second and 
  third, respectively, of the system's box directions non-periodic. Default 
  value is 'c'.  
  
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

Prepare for __surface_energy__ creates defect calculations based on the 
information provided by free-surface records and parent calculation-system-relax 
records. The default behavior is to retrieve all records of these types from a 
database, but limiters can be defined in the input script that restrict which 
are included. Alternatively, a list of pre-selected calculation-system-relax 
records from the database can be passed in if the calculation's prepare method 
is called directly. 

A calculation is prepared for every pair of the selected free-surface and 
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

- __surface_name__: [multiple values allowed] only free-surface records 
  associated with the named surface will be included. Default value places no 
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