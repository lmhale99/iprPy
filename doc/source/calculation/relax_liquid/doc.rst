relax_liquid calculation style
==============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The relax_liquid calculation style is designed to generate and
characterize a liquid phase configuration for an atomic potential based
on an initial configuration, target temperature and target pressure. The
calculation involves multiple stages of relaxation and computes the mean
squared displacement and radial distribution functions on the final
liquid.

Version notes
~~~~~~~~~~~~~

-  2022-10-??: Calculation created

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  No active checks are performed by this calculation to ensure that the
   system is liquid. Be sure to check the final atomic configurations.
   The thermo output can also provide a rough guideline in that you
   should see convergence of volume but not of the individual lx, ly, lz
   dimensions for a liquid phase.
-  If starting with a crystalline configuration, be sure to use an
   adequately high melt temperature and number of melt steps.
-  The temperature and volume equilibrium stages are designed to get the
   final nve system close to the target temperature and pressure, but
   they will not be exact. Be sure to check that the measured
   temperature and pressure are close to the targets.

Method and Theory
-----------------

This performs five stages of simulations to create and analyze a liquid
phase at a given temperature and pressure.

1. A “melt” stage is performed using npt at the target pressure and an
   elevated melt temperature.
2. A “cooling” stage is performed using npt in which the temperature is
   linearly reduced from the melt to the target temperature.
3. A “volume equilibrium” stage is performed using npt at the target
   temperature and pressure. Following the run, the system’s dimensions
   are equally scaled to the average volume.
4. A “temperature equilibrium” stage is performed using nvt at the
   target temperature. Following the run, the atomic velocities are
   scaled based on the expected total energy at the target temperature.
5. An “nve analysis” stage is performed in which the mean squared
   displacements of the atoms and the radial distribution function are
   measured.

Melt stage
~~~~~~~~~~

The melt stage subjects the initial configuration to an npt simulation
at the elevated melt temperature. This stage is meant to transform
initially crystalline system configurations into amorphous liquid
phases. As such, the melt temperature should be much higher than the
melting temperature of the initial crystal, and the number of MD steps
during this stage should be sufficiently high to allow for the phase
transformation to occur.

If the initial atomic configuration is already amorphous, this stage can
be skipped by setting meltsteps = 0. Also, if the initial configuration
already has velocities assigned to the atoms, you can use those
velocities by setting createvelocities = False. These two options make
it possible to run a single melt simulation that can be used as the
basis for all target temperatures. Note that createvelocities = True is
needed if you want to measure statistical error from multiple runs.

Cooling stage
~~~~~~~~~~~~~

The cooling stage runs npt and linearly scales the temperature from the
melt temperature to the target temperature. The larger the number of
coolsteps, the more gradual the change from melt to target temperatures
will be. This can be important if the target temperature is much smaller
than the melt temperature.

Similarly to the melt stage, this stage can be skipped by setting
coolsteps = 0. If meltsteps = coolsteps = 0 and createvelocities = True,
the atomic velocities will be created for the system at the target
temperature rather than the melt temperature. This allows for a generic
amorphous state to be used as the starting configuration.

Volume equilibration stage
~~~~~~~~~~~~~~~~~~~~~~~~~~

The volume equilibration stage runs npt at the target temperature and
pressure. It is meant to allow for the system to equilibrate at the
target temperature, then to obtain a time-averaged measurement of the
system’s volume. The average volume is computed from a specified number
of samples (volrelaxsamples) taken every 100 timesteps from the end of
this stage. The max value allowed for volrelaxsamples is volrelaxsteps /
100, but practically it should be noticeably smaller than this to ignore
measurements at the beginning of the stage where the system has not yet
equilibrated.

When this stage finishes, the volume of the configuration cell is
adjusted to the average volume computed by scaling each box length and
tilt by the same factor, s

.. math::  s = \left( \frac{ \left< vol \right> } {vol} \right)^\frac{1}{3} 

Temperature equilibration stage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The temperature equilibration stage runs nvt at the target temperature
for the system fixed at the computed average volume. This allows for the
system to equilibrate at the fixed volume and target temperature, and to
compute a target total energy, :math:`E_{target}`, that corresponds to
the system in equilibrium at the target temperature. :math:`E_{target}`
is computed based on time-averaged energy values from a specified number
of samples (temprelaxsamples) taken every 100 timesteps from the end of
this stage. The max value allowed for temprelaxsamples is temprelaxsteps
/ 100. Unlike the previous stage, the equilibration portion of this
stage is likely negligible, therefore it is less important to ignore the
initial measurements.

In LAMMPS, the adjustment is made by scaling all atomic velocities to a
temperature :math:`T_s` such that the current potential energy,
:math:`E_{pot}`, plus the kinetic energy for :math:`T_s` equals
:math:`E_{target}`

.. math::  E_{target} = E_{pot} + \frac{3}{2} N k_B T_s 

.. math::  T_s = \frac{2 \left( E_{target} - E_{pot} \right)}{3 N k_B} 

Two alternate methods for computing :math:`E_{target}` are implemented
and can be accessed with the temprelaxstyle option.

-  For temprelaxstyle = ‘te’, the target total energy is taken as the
   computed mean total energy

.. math::  E_{target} = \left< E_{total}\right>

-  For temprelaxstyle = ‘pe’, the target total energy is taken as the
   computed mean potential energy plus kinetic energy for the target
   temperature, :math:`T`

.. math::  E_{target} = \left< E_{pot} \right> + \frac{3}{2} N k_B T 

Limited tests show the two methods to result in mean temperatures in the
final stage that have roughly the same variation from the target
temperature, with ‘pe’ style giving slightly better results. As such,
both methods are included as options and ‘pe’ is set as the default.

Analysis stage
~~~~~~~~~~~~~~

The analysis stage runs nve with the system that has been adjusted to
the target volume and total energy from the last two stages. During this
stage, mean squared displacements and radial distribution function
calculations are performed that can be used to analyze the liquid phase
at the target temperature and pressure.

In addition to the analysis calculations, the average measured
temperature and pressure are reported, which can be used as verification
that the volume and temperature equilibration stages and adjustments
worked properly.
