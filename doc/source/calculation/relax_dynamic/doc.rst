relax_dynamic calculation style
===============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

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
-  2022-03-11: Notebook updated to reflect version 0.11. Restart
   capability added in.

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

Method and Theory
-----------------

An initial system (and corresponding unit cell system) is supplied with
box dimensions, :math:`a_i^0`, close to the equilibrium values. A LAMMPS
simulation then integrates the atomic positions and velocities for a
specified number of timesteps.

The calculation script allows for the use of different integration
methods:

-  nve integrates atomic positions without changing box dimensions or
   the system’s total energy.

-  npt integrates atomic positions and applies Nose-Hoover style
   thermostat and barostat (equilibriate to specified T and P).

-  nvt integrates atomic positions and applies Nose-Hoover style
   thermostat (equilibriate to specified T).

-  nph integrates atomic positions and applies Nose-Hoover style
   barostat (equilibriate to specified P).

-  nve+l integrates atomic positions and applies Langevin style
   thermostat (equilibriate to specified T).

-  nph+l integrates atomic positions and applies Nose-Hoover style
   barostat and Langevin style thermostat (equilibriate to specified T
   and P).

**Notes** on the different control schemes:

-  The Nose-Hoover barostat works by rescaling the box dimensions
   according to the measured system pressures.

-  The Nose-Hoover thermostat works by rescaling the atomic velocities
   according to the measured system temperature (kinetic energy). Cannot
   be used with a temperature of 0 K.

-  The Langevin thermostat works by modifying the forces on all atoms
   with both a dampener and a random temperature dependent fluctuation.
   Used at 0 K, only the force dampener is applied.

**Notes** on run parameter values. The proper time to reach equilibrium
(equilsteps), and sample frequency to ensure uncorrelated measurements
(thermosteps) is simulation dependent. They can be influenced by the
potential, timestep size, crystal structure, integration method,
presence of defects, etc. The default values of equilsteps = 20,000 and
thermosteps = 100 are based on general rule-of-thumb estimates for bulk
crystals and EAM potentials, and may or may not be adequate.
