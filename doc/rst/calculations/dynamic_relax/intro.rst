
Introduction
************

The dynamic_relax calculation dynamically relaxes an atomic
configuration for a sepcified number of timesteps. Upon completion,
the mean, <X>, and standard deviation, \sigma_X, of all thermo
properties, X, are computed for a specified range of times. This
method is meant to measure equilibrium properties of bulk materials,
both at zero K and at various temperatures.

**Disclaimer #1**: The calculation reports the standard deviation,
\sigma_X of the measured properties not the standard error of the
mean, \sigma_{<X>}. The two are related to each other according to

   \sigma_{<X>} = \sigma_X \sqrt{\frac{C}{N}}

,

where N is the number of samples taken of X, and C is a statistical
inefficiency due to the autocorrelation of the measurements with time.
Obtaining a proper estimate of \sigma_{<X>} requires either estimating
C from the raw thermo data (not done here), or only taking
measurements sporatically to ensure the samples are independent.

**Disclaimer #2**: Good (low error) results requires running large
simulations for a long time. The reasons for this are:

* Systems have to be large enough to avoid issues with fluctuations
  across the periodic boundaries.

* Runs must first let the systems equilibriate before meaningful
  measurements can be taken.

* The standard deviation, \sigma, of thermo properties is proportional
  to the number of atoms, N_a as \sigma \propto \frac{1}{\sqrt{N_a}}.

* The standard error, \sigma_x of thermo properties is proportional to
  the number of samples taken, N as \sigma_x \propto
  \frac{1}{\sqrt{N}}.
