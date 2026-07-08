## Theory and methodology

The Green-Kubo method allows for the viscosity to be estimated during an equilibrium molecular dynamics simulation using the autocorrelation of the off-diagonal (i.e. shear) pressure components.

$$ \eta = \frac{V}{k_B T} \int_0^{\infty}{\left<P_{\alpha\beta}(0) P_{\alpha\beta}(t)\right>dt} $$

In the simulation method, the pressure autocorrelations are computed using the LAMMPS "fix ave/correlate" command allowing for slightly smoother results by averaging the correlation over a few timesteps. The integral is then numerically estimated using the trapezoidal method.  As there are three shear pressures, this gives three separate estimates for the shear viscosity which are averaged together.  Once the integral is computed in LAMMPS, it is multiplied by the preceding factor to compute the shear viscosity.

The integral part of this calculation is known to converge very slowly, and therefore requires long simulation runs (typically > 1,000,000 steps) for good estimates.  Fluctuations in the integral can also be reduced by increasing the system dimensions.