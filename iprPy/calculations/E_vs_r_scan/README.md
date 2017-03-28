# E_vs_r_scan

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

The __E_vs_r_scan__ calculation creates a plot of the cohesive energy vs 
interatomic spacing, $r$, for a given atomic system. The system size is 
uniformly scaled ($b/a$ and $c/a$ ratios held fixed) and the energy is 
calculated at a number of sizes without relaxing the system. All box sizes 
corresponding to energy minima are identified. 

This calculation was created as a quick method for scanning the phase space of a
crystal structure with a given potential in order to identify starting guesses 
for further structure refinement calculations.

__Disclaimer #1__: the minima identified by this calculation do not guarantee 
that the associated crystal structure will be stable as no relaxation is 
performed by this calculation. Upon relaxation, the atomic positions and box 
dimensions may transform the system to a different structure

__Disclaimer #2__: it is possible that the calculation may miss an existing 
minima for a crystal structure if it is outside the range of $r$ values scanned,
or has $b/a$, $c/a$ values far from the ideal.

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

### Run Parameters

Provides parameters specific to the calculation at hand.

- __minimum_r__: specifies the minimum interatomic spacing, r, for the scan. 
  Default value is '2.0 angstrom'.

- __maximum_r__: specifies the maximum interatomic spacing, r, for the scan. 
  Default value is '6.0 angstrom'.

- __number_of_steps_r__: specifies the number of interatomic spacing values, r,
  to use. Default value is 200.

--------------------------------------------------------------------------------

## <a name="prepare"></a>Prepare description

Prepare for __E_vs_r_scan__ accesses a database and retrieves the 
LAMMPS-potential and crystal-prototype records. By default, this retrieves all 
records for both record types, but limiters can be defined in the input script 
that restrict which are included. 

For each possible combination of (LAMMPS-potential + crystal-prototype), a 
calculation is created for every unique assignment of the potential's element 
models to the prototype's atom types (unique sites). For example, if the 
potential contains two elements, say ['Al', 'Ni'], and the prototype has two 
atom types, then a calculation is created for that prototype for each of the 
following lists of symbols:

- ['Al', 'Al'] 

- ['Al', 'Ni']

- ['Ni', 'Al']

- ['Ni', 'Ni']

For each prepared calculation, a corresponding 
calculation-cohesive-energy-relation record is added to the database.

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

### Potential limiters

Limiters for which potentials to create calculations for. If none of these terms
are given, then calculations are prepared for every LAMMPS-potential record
stored in the database.

- __potential_element__: [multiple values allowed] only potentials with at least
  one element model specified will be included. Note that this limits by 
  potential not by element so all symbol combinations will still be explored for
  included potentials. Default value places no restrictions.

- __potential_name__: [multiple values allowed] only potentials with specified 
  names will be included. Default value places no restrictions.

- __potential_pair_style__: [multiple values allowed] only potentials of the 
  specified LAMMPS pair_styles will be included. Default value places no 
  restrictions.

### Prototype limiters:

Limiters for which crystal prototypes to create calculations for. If none of
these terms are given, then calculations are prepared for every 
crystal-prototype record stored in the database.

- __prototype_natypes__: [multiple values allowed] only crystal prototypes with
  the specified number of atom types (unique sites) will be included. Default 
  value places no restrictions.

- __prototype_name__: [multiple values allowed] only crystal prototypes with 
  specified names will be included. Default value places no restrictions.

- __prototype_spacegroup__: [multiple values allowed] only crystal prototypes 
  with the specified space group number will be included. Default value places 
  no restrictions.

- __prototype_crystalfamily__: [multiple values allowed] only crystal prototypes
  with the specified crystal family (cubic, hexagonal, etc.) will be included.
  Default value places no restrictions.

- __prototype_Pearsonsymbol__: [multiple values allowed] only crystal prototypes
  with the specified Pearson symbol will be included. Default value places no
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

- __minimum_r__: specifies the minimum interatomic spacing, r, for the scan. 
  Default value is '2.0 angstrom'.

- __maximum_r__: specifies the maximum interatomic spacing, r, for the scan. 
  Default value is '6.0 angstrom'.

- __number_of_steps_r__: specifies the number of interatomic spacing values, r,
  to use. Default value is 200.