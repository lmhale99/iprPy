## Input script parameters

This is a list of the input parameter names recognized by calc_dislocation_SDVPN.py.

### Global metadata parameters

- __branch__: assigns a group/branch descriptor to the calculation which can help with parsing results later.  Default value is 'main'.

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

### Gamma Surface Parameters

Specify which gamma surface results to load.

- __gammasurface_file__: the path to a file that contains a data model associated with an atomman.defect.GammaSurface object. Within the iprPy framework, this can be a calculation_stacking_fault_map_2D record.

### Elastic constants parameters

Specifies the computed elastic constants for the interatomic potential and crystal structure, relative to the loaded system's orientation.

- __elasticconstants_file__: the path to a record containing the elastic constants to use.  If neither this or the individual Cij components (below) are given and *load_style* is 'system_model', this will be set to *load_file*.
- __C11, C12, C13, C14, C15, C16, C22, C23, C24, C25, C26, C33, C34, C35, C36, C44, C45, C46, C55, C56, C66__: the individual elastic constants components in units of pressure.  If the loaded system's orientation is the standard setting for the crystal type, then missing values will automatically be filled in. Example: if the loaded system is a cubic prototype, then only C11, C12 and C44 need be specified.
- Isotropic moduli: the elastic constants for an isotropic material can be defined using any two of the following
  - __C_M__: P-wave modulus (units of pressure).  
  - __C_lambda__: Lame's first parameter (units of pressure).
  - __C_mu__: shear modulus (units of pressure).
  - __C_E__: Young's modulus (units of pressure).
  - __C_nu__: Poisson's ratio (unitless).
  - __C_K__: bulk modulus (units of pressure).

### Dislocation defect parameters

Defines a unique dislocation type and orientation

- __dislocation_file__: the path to a dislocation_monopole record file that contains a set of input parameters associated with a specific dislocation.
- __dislocation_slip_hkl__: three integers specifying the Miller (hkl) slip plane for the dislocation.
- __dislocation_Î¾_uvw__: three integers specifying the Miller \[uvw\] line vector direction for the dislocation.  The angle between burgers and Î¾_uvw determines the dislocation's character
- __dislocation_burgers__: three floating point numbers specifying the crystallographic Miller Burgers vector for the dislocation.
- __dislocation_m__ three floats for the Cartesian vector of the final system that the dislocation solution's m vector (in-plane, perpendicular to Î¾) should align with.  Limited to being parallel to one of the three Cartesian axes.  
- __dislocation_n__ three floats for the Cartesian vector of the final system that the dislocation solution's n vector (slip plane normal) should align with.  Limited to being parallel to one of the three Cartesian axes.
- __dislocation_shift__: three floating point numbers specifying a rigid body shift to apply to the atoms in the system. This controls how the atomic positions align with the ideal position of the dislocation core, which is at coordinates (0,0) for the two Cartesian axes aligned with m and n.
- __dislocation_shiftscale__: boolean indicating if the *dislocation_shift* value should be absolute (False) or scaled relative to the rotated cell used to construct the system.
- __dislocation_shiftindex__: integer alternate to specifying shift values, the shiftindex allows for one of the identified suggested shift values to be used that will position the slip plane halfway between two planes of atoms.  Note that shiftindex values only shift atoms in the slip plane normal direction and may not be the ideal positions for some dislocation cores.
- __sizemults__: three integers specifying the box size multiplications to use.
- __amin__: floating point number stating the minimum width along the a direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __bmin__: floating point number stating the minimum width along the b direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.
- __cmin__: floating point number stating the minimum width along the c direction that the system must be.  The associated sizemult value will be increased if necessary.  Default value is 0.0.

### Units for input/output values

Specifies the units for various physical quantities to use when saving values to the results record file. Also used as the default units for parameters in this input parameter file.

- __length_unit__: defines the unit of length for results, and input parameters if not directly specified.  Default value is 'angstrom'.
- __energy_unit__: defines the unit of energy for results, and input parameters if not directly specified.  Default value is 'eV'.
- __pressure_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'GPa'.
- __force_unit__: defines the unit of pressure for results, and input parameters if not directly specified.  Default value is 'eV/angstrom'.

### Run parameters

Provides parameters specific to the calculation at hand.  See atomman.defect.SDVPN documentation for more details on these parameters.

- __xmax__: The maximum value of the x-coordinates to use for the points where the disregistry is evaluated.  The solution is centered around x=0, therefore this also corresponds to the minimum value of x used.  The set of x-coordinates used is fully defined by giving at least two of xmax, xstep and xnum.
- __xstep__: The step size (delta x) value between the x-coordinates used to evaluate the disregistry.  The set of x-coordinates used is fully defined by giving at least two of xmax, xstep and xnum.
- __xnum__: The total number of x-coordinates at which to evaluate the disregistry.  The set of x-coordinates used is fully defined by giving at least two of xmax, xstep and xnum.
- __minimize_style__: The scipy.optimize.minimize method style to use when solving for the disregistry.  Default value is 'Powell', which seems to do decently well for this problem.
- __minimize_options__: Allows for the specification of the options dictionary used by scipy.optimize.minimize. This is given as "key value key value...".
- __minimize_cycles__: Specifies the number of times to run the minimization in succession.  The minimization algorithms used by the underlying scipy code often benefit from restarting and rerunning the minimized configuration to achive a better fit.  Default value is 10.
- __cutofflongrange__: The radial cutoff (in distance units) to use for the long-range elastic energy.  The long-range elastic energy is configuration-independent, so this value changes the dislocation's energy but not the computed disregistry profile. Default value is 1000 Angstroms.
- __tau_xy__: Shear stress (in units of pressure) to apply to the system. Default value is 0 GPa.
- __tau_yy__: Normal stress (in units of pressure) to apply to the system. Default value is 0 GPa.
- __tau_yz__: Shear stress (in units of pressure) to apply to the system. Default value is 0 GPa.
- __alpha__: Coefficient(s) (in pressure/length units) of the non-local energy correction term to use.  Default value is 0.0, meaning this correction is not applied.
- __beta_xx, beta_yy, beta_zz, beta_xy, beta_xz, beta_yz__: Components of the surface energy coefficient tensor (in units pressure-length) to use. Default value is 0.0 GPa-Angstrom for all, meaning this correction is not applied.
- __cdiffelastic, cdiffsurface, cdiffstress__: Booleans indicating how the dislocation density (derivative of disregistry) is computed within the elastic, surface and stress terms, respectively. If True, central difference is used, otherwise only the change between the current and previous points is used. Default values are True for cdiffsurface, and False for the other two.
- __halfwidth__: The arctan disregistry halfwidth (in length units) to use for creating the initial disregistry guess.
- __normalizedisreg__: Boolean indicating how the disregistry profile is handled.  If True (default), the disregistry is scaled such that the minimum x value has a disregistry of 0 and the maximum x value has a disregistry equal to the dislocation's Burgers vector.  Note that the disregistry for these endpoints is fixed, so if you use False the initial disregistry should be close to the final solution.
- __fullstress__: Boolean indicating which of two stress formulas to use.  True uses the original full formulation, while False uses a newer, simpler representation.  Default value is True.
