Introduction
============

The relax_dynamic calculation style dynamically relaxes an atomic
configuration for a specified number of timesteps. Upon completion, the
mean, :math:`\langle X \rangle`, and standard deviation,
:math:`\sigma_X`, of all thermo properties, :math:`X`, are computed for
a specified range of times. This method is meant to measure equilibrium
properties of bulk materials, both at zero K and at various
temperatures.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definition streamlined.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The calculation reports the standard deviation, :math:`\sigma_X` of
   the measured properties not the standard error of the mean,
   :math:`\sigma_{\langle X \rangle}`. The two are related to each other
   according to
   :math:`\sigma_{\langle X \rangle} = \sigma_X \sqrt{\frac{C}{N}}`,
   where :math:`N` is the number of samples taken of :math:`X`, and
   :math:`C` is a statistical inefficiency due to the autocorrelation of
   the measurements with time. Obtaining a proper estimate of
   :math:`\sigma_{\langle X \rangle}` requires either estimating
   :math:`C` from the raw thermo data (not done here), or only taking
   measurements sporadically to ensure the samples are independent.
-  Good (low error) results requires running large simulations for a
   long time. The reasons for this are:

   -  Systems have to be large enough to avoid issues with fluctuations
      across the periodic boundaries.
   -  Runs must first let the systems equilibrate before meaningful
      measurements can be taken.
   -  The standard deviation, :math:`\sigma`, of thermo properties is
      proportional to the number of atoms, :math:`N_a` as
      :math:`\sigma \propto \frac{1}{\sqrt{N_a}}`.
   -  The standard error, :math:`\sigma_x` of thermo properties is
      proportional to the number of samples taken, :math:`N` as
      :math:`\sigma_x \propto \frac{1}{\sqrt{N}}`.
