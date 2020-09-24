Input script parameters
-----------------------

This is a list of the input parameter names recognized by
calc_dislocation_SDVPN.py.

Global metadata parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  **branch**: assigns a group/branch descriptor to the calculation
   which can help with parsing results later. Default value is ‘main’.

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

Gamma Surface Parameters
~~~~~~~~~~~~~~~~~~~~~~~~

Specify which gamma surface results to load.

-  **gammasurface_file**: the path to a file that contains a data model
   associated with an atomman.defect.GammaSurface object. Within the
   iprPy framework, this can be a calculation_stacking_fault_map_2D
   record.

Elastic constants parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifies the computed elastic constants for the interatomic potential
and crystal structure, relative to the loaded system’s orientation.

-  **elasticconstants_file**: the path to a record containing the
   elastic constants to use. If neither this or the individual Cij
   components (below) are given and *load_style* is ‘system_model’, this
   will be set to *load_file*.
-  **C11, C12, C13, C14, C15, C16, C22, C23, C24, C25, C26, C33, C34,
   C35, C36, C44, C45, C46, C55, C56, C66**: the individual elastic
   constants components in units of pressure. If the loaded system’s
   orientation is the standard setting for the crystal type, then
   missing values will automatically be filled in. Example: if the
   loaded system is a cubic prototype, then only C11, C12 and C44 need
   be specified.
-  Isotropic moduli: the elastic constants for an isotropic material can
   be defined using any two of the following

   -  **C_M**: P-wave modulus (units of pressure).
   -  **C_lambda**: Lame’s first parameter (units of pressure).
   -  **C_mu**: shear modulus (units of pressure).
   -  **C_E**: Young’s modulus (units of pressure).
   -  **C_nu**: Poisson’s ratio (unitless).
   -  **C_K**: bulk modulus (units of pressure).

Dislocation defect parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines a unique dislocation type and orientation

-  **dislocation_file**: the path to a dislocation_monopole record file
   that contains a set of input parameters associated with a specific
   dislocation.
-  **dislocation_slip_hkl**: three integers specifying the Miller (hkl)
   slip plane for the dislocation.
-  **dislocation_Î¾_uvw**: three integers specifying the Miller [uvw]
   line vector direction for the dislocation. The angle between burgers
   and Î¾_uvw determines the dislocation’s character
-  **dislocation_burgers**: three floating point numbers specifying the
   crystallographic Miller Burgers vector for the dislocation.
-  **dislocation_m** three floats for the Cartesian vector of the final
   system that the dislocation solution’s m vector (in-plane,
   perpendicular to Î¾) should align with. Limited to being parallel to
   one of the three Cartesian axes.
-  **dislocation_n** three floats for the Cartesian vector of the final
   system that the dislocation solution’s n vector (slip plane normal)
   should align with. Limited to being parallel to one of the three
   Cartesian axes.
-  **dislocation_shift**: three floating point numbers specifying a
   rigid body shift to apply to the atoms in the system. This controls
   how the atomic positions align with the ideal position of the
   dislocation core, which is at coordinates (0,0) for the two Cartesian
   axes aligned with m and n.
-  **dislocation_shiftscale**: boolean indicating if the
   *dislocation_shift* value should be absolute (False) or scaled
   relative to the rotated cell used to construct the system.
-  **dislocation_shiftindex**: integer alternate to specifying shift
   values, the shiftindex allows for one of the identified suggested
   shift values to be used that will position the slip plane halfway
   between two planes of atoms. Note that shiftindex values only shift
   atoms in the slip plane normal direction and may not be the ideal
   positions for some dislocation cores.
-  **sizemults**: three integers specifying the box size multiplications
   to use.
-  **amin**: floating point number stating the minimum width along the a
   direction that the system must be. The associated sizemult value will
   be increased if necessary. Default value is 0.0.
-  **bmin**: floating point number stating the minimum width along the b
   direction that the system must be. The associated sizemult value will
   be increased if necessary. Default value is 0.0.
-  **cmin**: floating point number stating the minimum width along the c
   direction that the system must be. The associated sizemult value will
   be increased if necessary. Default value is 0.0.

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

Run parameters
~~~~~~~~~~~~~~

Provides parameters specific to the calculation at hand. See
atomman.defect.SDVPN documentation for more details on these parameters.

-  **xmax**: The maximum value of the x-coordinates to use for the
   points where the disregistry is evaluated. The solution is centered
   around x=0, therefore this also corresponds to the minimum value of x
   used. The set of x-coordinates used is fully defined by giving at
   least two of xmax, xstep and xnum.
-  **xstep**: The step size (delta x) value between the x-coordinates
   used to evaluate the disregistry. The set of x-coordinates used is
   fully defined by giving at least two of xmax, xstep and xnum.
-  **xnum**: The total number of x-coordinates at which to evaluate the
   disregistry. The set of x-coordinates used is fully defined by giving
   at least two of xmax, xstep and xnum.
-  **minimize_style**: The scipy.optimize.minimize method style to use
   when solving for the disregistry. Default value is ‘Powell’, which
   seems to do decently well for this problem.
-  **minimize_options**: Allows for the specification of the options
   dictionary used by scipy.optimize.minimize. This is given as “key
   value key value…”.
-  **minimize_cycles**: Specifies the number of times to run the
   minimization in succession. The minimization algorithms used by the
   underlying scipy code often benefit from restarting and rerunning the
   minimized configuration to achive a better fit. Default value is 10.
-  **cutofflongrange**: The radial cutoff (in distance units) to use for
   the long-range elastic energy. The long-range elastic energy is
   configuration-independent, so this value changes the dislocation’s
   energy but not the computed disregistry profile. Default value is
   1000 Angstroms.
-  **tau_xy**: Shear stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **tau_yy**: Normal stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **tau_yz**: Shear stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **alpha**: Coefficient(s) (in pressure/length units) of the non-local
   energy correction term to use. Default value is 0.0, meaning this
   correction is not applied.
-  **beta_xx, beta_yy, beta_zz, beta_xy, beta_xz, beta_yz**: Components
   of the surface energy coefficient tensor (in units pressure-length)
   to use. Default value is 0.0 GPa-Angstrom for all, meaning this
   correction is not applied.
-  **cdiffelastic, cdiffsurface, cdiffstress**: Booleans indicating how
   the dislocation density (derivative of disregistry) is computed
   within the elastic, surface and stress terms, respectively. If True,
   central difference is used, otherwise only the change between the
   current and previous points is used. Default values are True for
   cdiffsurface, and False for the other two.
-  **halfwidth**: The arctan disregistry halfwidth (in length units) to
   use for creating the initial disregistry guess.
-  **normalizedisreg**: Boolean indicating how the disregistry profile
   is handled. If True (default), the disregistry is scaled such that
   the minimum x value has a disregistry of 0 and the maximum x value
   has a disregistry equal to the dislocation’s Burgers vector. Note
   that the disregistry for these endpoints is fixed, so if you use
   False the initial disregistry should be close to the final solution.
-  **fullstress**: Boolean indicating which of two stress formulas to
   use. True uses the original full formulation, while False uses a
   newer, simpler representation. Default value is True.
