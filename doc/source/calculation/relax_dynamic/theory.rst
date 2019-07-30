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
