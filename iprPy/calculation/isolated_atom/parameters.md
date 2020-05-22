## Input script parameters

This is a list of the input parameter names recognized by the calculation script.

### Command lines for LAMMPS and MPI

Provides the external commands for running LAMMPS and MPI.

- __lammps_command__: the path to the executable for running LAMMPS on your system.  Don't include command line options.

- __mpi_command__: the path to the MPI executable and any command line options to use for calling LAMMPS to run in parallel on your system. Default value is None (run LAMMPS as a serial process).

### Potential definition and directory containing associated files

Provides the information associated with an interatomic potential implemented for LAMMPS.

- __potential_file__: the path to the potential_LAMMPS data model used by atomman to generate the proper LAMMPS commands for an interatomic potential.

- __potential_dir__: the path to the directory containing any potential artifacts (eg. eam.alloy setfl files) that are used. If not given, then any required files are expected to be in the working directory where the calculation is executed.

### Units for input/output values

Specifies the units for various physical quantities to use when saving values to the results record file. Also used as the default units for parameters in this input parameter file.

- __length_unit__: defines the unit of length for results, and input parameters if not directly specified.  Default value is 'angstrom'.

- __energy_unit__: defines the unit of energy for results, and input parameters if not directly specified.  Default value is 'eV'.

- __pressure_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'GPa'.

- __force_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'eV/angstrom'.
