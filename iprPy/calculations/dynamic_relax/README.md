# dynamic_relax

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

Version: 2017-03-23

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
--------------------------------------------------------------------------------

## Contents

- [Calculation description](#calc)

- [Calculation input parameter names](#calc-in)

- [Prepare description](#prepare)

- [Prepare input parameter names](#prepare-in)

--------------------------------------------------------------------------------

## <a name="calc"></a>Calculation description

The __dynamic_relax__ calculation dynamically relaxes an atomic configuration, 
including the box dimensions. This is accomplished by MD iterations at a 
temperature and pressure for a specified number of timesteps. Upon completion, 
the mean and estimated error of the mean is evaluated for all box dimensions 
taking the time autocorrelation into consideration. 

__Disclaimer #1__: Good (low error) results requires running large simulations 
for a long time. At the very least, systems have to be large enough to avoid 
issues with fluctuations across the periodic boundaries, and must last long 
enough that the system reaches equilibrium, and enough independent samples are
taken after equilibrium for a statistically meaningful measurement. Basically,
the larger and longer the better, but the more computationally expensive.

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
  value is '10 10 10'.

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

- __temperature__: temperature in Kelvin at which to run the MD integration 
  scheme at. Default value is 0.

- __pressure_xx, pressure_yy, pressure_zz__: specifies the normal pressures to
  relax the box to. Default values are '0 GPa' for all.

- __integrator__: specifies which MD integration scheme to use. Default value is
  'nph+l' for temperature = 0, and 'npt' otherwise.
  
- __runsteps__: specifies how many timesteps to integrate the system. Default 
  value is 100000.
  
- __thermosteps__: specifies how often LAMMPS prints the system-wide thermo
  data. Default value is runsteps/1000, or 1 if runsteps is less than 1000.

- __dumpsteps__: specifies how often LAMMPS saves the atomic configuration to a
  LAMMPS dump file. Default value is runsteps, meaning only the first and last
  states are saved.

- __equilsteps__: specifies how many timesteps are ignored as equilibration time
  when computing the mean box parameters. Default value is 10000.

- __randomseed__: provides a random number seed to generating the initial atomic
  velocities. Default value gives a random number as the seed.
  
--------------------------------------------------------------------------------

## <a name="prepare"></a>Prepare description

Prepare for __dynamic_relax__ accesses a database and retrieves parent 
calculation-cohesive-energy-relation records. By default, this retrieves all 
records of this type, but limiters can be defined in the input script that 
restrict which are included. Each calculation-cohesive-energy-relation record is
associated with a single combination of interatomic potential, crystal prototype,
and list of element symbols, and provides a list of atomic configurations near 
local energy minima.

The prepare script uses the energy minima configurations as the initial guesses
for structures in prepared dynamic_relax calculations. Multiple temperature and 
sizemults values can also be supplied, resulting in one prepared calculation for
each combination of run parameters and initial configuration. 

For each prepared calculation, a corresponding calculation-dynamic-relax record
is added to the database.

--------------------------------------------------------------------------------

## <a name="prepare-in"></a>Prepare input parameter names

This is a list of the input parameter names recognized by the prepare script.

### Database and run_directory

These terms define the access parameters for the database to get/save records,
and the location of the run_directory where the prepared calculation folders are
to be added. Note that these parameters are not needed when preparing from the
iprPy inline command or from iprPy.Calculation.prepare().

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

### System Manipulations

- __sizemults__: [multiple values allowed] multiplication parameters for 
  making a supercell of the loaded system. This may either be a list of three or
  six integer numbers. Default value is '10 10 10'.

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

- __temperature__: [multiple values allowed] temperature in Kelvin at which to 
  run the MD integration scheme at. Default value is 0.

- __pressure_xx, pressure_yy, pressure_zz__: specifies the normal pressures to
  relax the box to. Default values are '0 GPa' for all.

- __integrator__: specifies which MD integration scheme to use. Default value is
  'nph+l' for temperature = 0, and 'npt' otherwise.
  
- __runsteps__: specifies how many timesteps to integrate the system. Default 
  value is 100000.
  
- __thermosteps__: specifies how often LAMMPS prints the system-wide thermo
  data. Default value is runsteps/1000, or 1 if runsteps is less than 1000.

- __dumpsteps__: specifies how often LAMMPS saves the atomic configuration to a
  LAMMPS dump file. Default value is runsteps, meaning only the first and last
  states are saved.

- __equilsteps__: specifies how many timesteps are ignored as equilibration time
  when computing the mean box parameters. Default value is 10000.

- __randomseed__: provides a random number seed to generating the initial atomic
  velocities. Default value gives a random number as the seed.