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
