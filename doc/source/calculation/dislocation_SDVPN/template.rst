dislocation_SDVPN Input Terms
=============================

Calculation Metadata
--------------------

Specifies metadata descriptors common to all calculation styles.

-  **branch**: A metadata group name that the calculation can be parsed
   by. Primarily meant for differentiating runs with different settings
   parameters.

Initial System Configuration
----------------------------

Specifies the file and options to load for the initial atomic
configuration.

-  **load_file**: The path to the initial configuration file to load.
-  **load_style**: The atomman.load() style indicating the format of the
   load_file.
-  **load_options**: A space-delimited list of key-value pairs for
   optional style-specific arguments used by atomman.load().
-  **family**: A metadata descriptor for relating the load_file back to
   the original crystal structure or prototype that the load_file was
   based on. If not given, will use the family field in load_file if
   load_style is ‘system_model’, or the file’s name otherwise.
-  **symbols**: A space-delimited list of the potential’s atom-model
   symbols to associate with the loaded system’s atom types. Required if
   load_file does not contain symbol/species information.
-  **box_parameters**: Specifies new box parameters to scale the loaded
   configuration by. Can be given either as a list of three or six
   numbers: ‘a b c’ for orthogonal boxes, or ‘a b c alpha beta gamma’
   for triclinic boxes. The a, b, c parameters are in units of length
   and the alpha, beta, gamma angles are in degrees.

Elastic Constants
-----------------

Specifies the computed elastic constants for the interatomic potential
and crystal structure, relative to the loaded system’s orientation. If
the values are specified with the Voigt Cij terms and the system is in a
standard setting for a crystal type, then only the unique Cij values for
that crystal type are necessary. If isotropic values are used, only two
idependent parameters are necessary.

-  **elasticconstants_file**: The path to a record containing the
   elastic constants to use. If neither this or the individual Cij
   components (below) are given and load_style is ‘system_model’, this
   will be set to load_file.
-  **C11**: The C11 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C12**: The C12 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C13**: The C13 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C14**: The C14 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C15**: The C15 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C16**: The C16 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C22**: The C22 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C23**: The C23 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C24**: The C24 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C25**: The C25 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C26**: The C26 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C33**: The C33 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C34**: The C34 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C35**: The C35 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C36**: The C36 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C44**: The C44 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C45**: The C45 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C46**: The C46 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C55**: The C55 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C56**: The C56 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C66**: The C66 component of the 6x6 Cij Voigt Cij elastic stiffness
   tensor (units of pressure).
-  **C_M**: The isotropic P-wave modulus (units of pressure).
-  **C_lambda**: The isotropic Lame’s first parameter (units of
   pressure).
-  **C_mu**: The isotropic shear modulus (units of pressure).
-  **C_E**: The isotropic Young’s modulus (units of pressure).
-  **C_nu**: The isotropic Poisson’s ratio (unitless).
-  **C_K**: The isotropic bulk modulus (units of pressure).

Gamma Surface
-------------

Specifies the gamma surface results to load.

-  **gammasurface_file**: The path to a file that contains a data model
   associated with an atomman.defect.GammaSurface object. Can be a
   record for a finished stacking_fault_map_2D calculation.

Dislocation
-----------

Specifies the parameter set that defines a dislocation type and how to
orient it relative to the atomic system.

-  **dislocation_file**: The path to a dislocation record file that
   collects the parameters for a specific dislocation type.
-  **dislocation_slip_hkl**: The Miller (hkl) slip plane for the
   dislocation given as three space-delimited integers.
-  **dislocation_ξ_uvw**: The Miller [uvw] line vector direction for the
   dislocation given as three space-delimited integers. The angle
   between burgers and ξ_uvw determines the dislocation’s character.
-  **dislocation_burgers**: The Miller Burgers vector for the
   dislocation given as three space-delimited floats.
-  **dislocation_m**: The Cartesian vector of the final system that the
   dislocation solution’s m vector (in-plane, perpendicular to ξ) should
   align with. Given as three space-delimited numbers. Limited to
   beingparallel to one of the three Cartesian axes.
-  **dislocation_n**: The Cartesian vector of the final system that the
   dislocation solution’s n vector (slip plane normal) should align
   with. Given as three space-delimited numbers. Limited to
   beingparallel to one of the three Cartesian axes.
-  **dislocation_shift**: A rigid body shift to apply to the atoms in
   the system after it has been rotated to the correct orientation. This
   controls where the dislocation is placed relative to the atomic
   positions as the dislocation line is always inserted at coordinates
   (0,0) for the two Cartesian axes aligned with m and n. Specified as
   three floating point numbers.
-  **dislocation_shiftscale**: boolean indicating if the
   dislocation_shift value is a Cartesian vector (False, default) or if
   it is scaled relative to the rotated cell’s box parameters prior to
   applying sizemults.
-  **dislocation_shiftindex**: An integer that if given will result in a
   shift being automatically determined and used such that the
   dislocation’s slip plane will be positioned halfway between two
   atomic planes. Changing the integer value changes which set of planes
   the slip plane is positioned between. Note that shiftindex values
   only shift atoms in the slip plane normal direction and therefore may
   not be the ideal positions for some dislocation cores.
-  **sizemults**: Multiplication parameters to construct a supercell
   from the rotated system. Limited to three values for dislocation
   generation. Values must be even for the two box vectors not aligned
   with the dislocation line. The system will be replicated equally in
   the positive and negative directions for those two box vectors.
-  **amin**: Specifies a minimum width in length units that the
   resulting system’s a box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.
-  **bmin**: Specifies a minimum width in length units that the
   resulting system’s b box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.
-  **cmin**: Specifies a minimum width in length units that the
   resulting system’s c box vector must have. The associated sizemult
   value will be increased if necessary to ensure this. Default value is
   0.0.

Input/Output Units
------------------

Specifies the default units to use for the other input keys and to use
for saving to the results file.

-  **length_unit**: The unit of length to use. Default value is
   ‘angstrom’.
-  **pressure_unit**: The unit of pressure to use. Default value is
   ‘GPa’.
-  **energy_unit**: The unit of energy to use. Default value is ‘eV’.
-  **force_unit**: The unit of force to use. Default value is
   ‘eV/angstrom’.

Run Parameters
--------------

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
-  **xscale**: Boolean indicating if xmax and xstep are taken in
   angstroms (False) or relative to the unit cell’s a box vector (True).
   Default value is False.
-  **minimize_style**: The scipy.optimize.minimize method style to use
   when solving for the disregistry. Default value is ‘Powell’, which
   seems to do decently well for this problem.
-  **minimize_options**: Allows for the specification of the options
   dictionary used by scipy.optimize.minimize. This is given as ‘key
   value key value…’.
-  **minimize_cycles**: Specifies the number of times to run the
   minimization in succession. The minimization algorithms used by the
   underlying scipy code often benefit from restarting and rerunning the
   minimized configuration to achive a better fit. Default value is 10.
-  **cutofflongrange**: The radial cutoff (in distance units) to use for
   the long-range elastic energy. The long-range elastic energy is
   configuration-independent, so this value changes the dislocation’s
   energy but not the computed disregistry profile. Default value is
   1000 angstroms.
-  **tau_xy**: Shear stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **tau_yy**: Normal stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **tau_yz**: Shear stress (in units of pressure) to apply to the
   system. Default value is 0 GPa.
-  **alpha**: Coefficient(s) (in pressure/length units) of the non-local
   energy correction term to use. Default value is 0.0, meaning this
   correction is not applied.
-  **beta_xx**: The xx component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **beta_yy**: The yy component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **beta_zz**: The zz component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **beta_xy**: The xy component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **beta_xz**: The xz component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **beta_yz**: The yz component of the surface energy coefficient
   tensor (in units pressure-length) to use. Default value is 0.0
   GPa-Angstrom.
-  **cdiffelastic**: Boolean indicating if the dislocation density is
   computed using central difference for the elastic term. Default value
   is False
-  **cdiffsurface**: Boolean indicating if the dislocation density is
   computed using central difference for the surface term. Default value
   is True
-  **cdiffstress**: Boolean indicating if the dislocation density is
   computed using central difference for the stress term. Default value
   is False
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
