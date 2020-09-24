Input script parameters
-----------------------

This is a list of the input parameter names recognized by
calc_stacking_fault_static.py.

Global metadata parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **branch**: assigns a group/branch descriptor to the calculation
   which can help with parsing results later. Default value is ‘main’.

Command lines for LAMMPS and MPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the external commands for running LAMMPS and MPI.

-  **lammps_command**: the path to the executable for running LAMMPS on
   your system. Don’t include command line options.
-  **mpi_command**: the path to the MPI executable and any command line
   options to use for calling LAMMPS to run in parallel on your system.
   Default value is None (run LAMMPS as a serial process).

Potential definition and directory containing associated files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the information associated with an interatomic potential
implemented for LAMMPS.

-  **potential_file**: the path to the potential_LAMMPS data model used
   by atomman to generate the proper LAMMPS commands for an interatomic
   potential.
-  **potential_dir**: the path to the directory containing any potential
   artifacts (eg. eam.alloy setfl files) that are used. If not given,
   then any required files are expected to be in the working directory
   where the calculation is executed.

Initial system configuration to load
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the information associated with loading an atomic
configuration.

-  **load_file**: the path to the initial configuration file being read
   in.
-  **load_style**: the style/format for the load_file. The style can be
   any file type supported by atomman.load()
-  **load_options**: a list of key-value pairs for the optional
   style-dependent arguments used by atomman.load().
-  **family**: specifies the configuration family to associate with the
   loaded file. This is typically a crystal structure/prototype
   identifier that helps with linking calculations on the same material
   together. If not given and the load_style is system_model, then the
   family will be taken from the file if included. Otherwise, the family
   will be taken as load_file stripped of path and extension.
-  **symbols**: a space-delimited list of the potential’s atom-model
   symbols to associate with the loaded system’s atom types. Required if
   load_file does not contain this information.
-  **box_parameters**: *Note that this parameter has no influence on
   this calculation.* allows for the specification of new box parameters
   to scale the loaded configuration by. This is useful for running
   calculations based on prototype configurations that do not contain
   material-specific dimensions. Can be given either as a list of three
   or six numbers, with an optional unit of length at the end. If the
   unit of length is not given, the specified length_unit (below) will
   be used.

   -  a b c (unit): for orthogonal boxes.
   -  a b c alpha beta gamma (unit): for triclinic boxes. The angles are
      taken in degrees.

Stacking Fault Defect Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines a stacking fault defect system to construct and analyze.

-  **stackingfault_file**: the path to a stacking-fault record file that
   contains a set of input parameters associated with a specific
   generalized stacking fault plane.
-  **stackingfault_hkl** three integers for the Miller (hkl) or
   Miller-Bravais (hkil) plane to create the free surface on.
-  **stackingfault_a1vect_uvw, stackingfault_a2vect_uvw**: three
   floating point numbers each that define the two directions of
   shifting associated with the 2D generalized stacking fault. This is
   taken as a crystallographic vector relative to the box vectors of the
   initial load configuration file. This is done so that these values
   have crystallographic meaning instead of just numerical meaning. Both
   vectors should be within the fault plane. Ideally, they should be set
   such that applying a full shiftvector shifts the system from one
   perfect periodic configuration to the next.
-  **stackingfault_cellsetting** indicates the conventional cell setting
   for the crystal to use for specifying *surface_hkl* if the given unit
   cell is primitive. Values are ‘p’, ‘c’, ‘i’, ‘a’, ‘b’ and ‘c’.
   Default value is ‘p’, i.e. the hkl values will be taken as directly
   related to the loaded unit cell.
-  **stackingfault_cutboxvector** specifies which of the three box
   vectors (‘a’, ‘b’, or ‘c’) is to be made non-periodic to create the
   free surface. Default value is ‘c’.
-  **stackingfault_shiftindex**: integer indicating which rigid body
   shift to apply to the system before making the cut. This effectively
   controls the atomic termination planes.
-  **stackingfault_faultpos**: specifies a fractional coordinate from 0
   to 1 indicating where along the planeaxis direction in the crystal to
   position the fault plane. Default value is 0.5, which if
   stackingfault_even is True will result in the same termination planes
   at the free surface and the stacking fault.
-  **sizemults**: three integers specifying the box size multiplications
   to use.
-  **stackingfault_minwidth**: floating point number stating the minimum
   width along the cutboxvector direction that the system must be. The
   associated sizemult value will be increased if necessary. Default
   value is 0.0.
-  **stackingfault_even**: boolean indicating if the number of replicas
   in the cutboxvector direction must be even. Default value is False.

Units for input/output values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the units for various physical quantities to use when saving
values to the results record file. Also used as the default units for
parameters in this input parameter file.

-  **length_unit**: defines the unit of length for results, and input
   parameters if not directly specified. Default value is ‘angstrom’.
-  **energy_unit**: defines the unit of energy for results, and input
   parameters if not directly specified. Default value is ‘eV’.
-  **pressure_unit**: defines the unit of pressure for results, and
   input parameters if not directly specified. Default value is ‘GPa’.
-  **force_unit**: defines the unit of pressure for results, and input
   parameters if not directly specified. Default value is ‘eV/angstrom’.

LAMMPS minimization parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the run parameters associated with an energy/force
minimization in LAMMPS.

-  **energytolerance**: specifies the energy tolerance to use for the
   minimization. This value is unitless and corresponds to the etol term
   for the `LAMMPS minimize
   command. <http://lammps.sandia.gov/doc/minimize.html>`__ Default
   value is 0.
-  **forcetolerance**: specifies the force tolerance to use for the
   minimization. This value is in force units and corresponds to the
   ftol term for the `LAMMPS minimize
   command. <http://lammps.sandia.gov/doc/minimize.html>`__ Default
   value is ‘1.0e-10 eV/angstrom’.
-  **maxiterations**: specifies the maximum number of iterations to use
   for the minimization. This value corresponds to the maxiter term for
   the `LAMMPS minimize
   command. <http://lammps.sandia.gov/doc/minimize.html>`__ Default
   value is 1000.
-  **maxevaluations**: specifies the maximum number of iterations to use
   for the minimization. This value corresponds to the maxeval term for
   the `LAMMPS minimize
   command. <http://lammps.sandia.gov/doc/minimize.html>`__ Default
   value is 10000.
-  **maxatommotion**: specifies the maximum distance that any atom can
   move during a minimization iteration. This value is in units length
   and corresponds to the dmax term for the `LAMMPS min_modify
   command. <http://lammps.sandia.gov/doc/min_modify.html>`__ Default
   value is ‘0.01 angstrom’.

Run parameters
~~~~~~~~~~~~~~

Provides parameters specific to the calculation at hand.

-  **stackingfault_a1, stackingfault_a2**: specifies the fractional
   shifts to apply along the two shift vectors.
