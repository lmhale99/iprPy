E_vs_r_scan calculation style
=============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The E_vs_r_scan calculation style calculation creates a plot of the
cohesive energy vs interatomic spacing, :math:`r`, for a given atomic
system. The system size is uniformly scaled (:math:`b/a` and :math:`c/a`
ratios held fixed) and the energy is calculated at a number of sizes
without relaxing the system. All box sizes corresponding to energy
minima are identified.

This calculation was created as a quick method for scanning the phase
space of a crystal structure with a given potential in order to identify
starting guesses for further structure refinement calculations.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definitions streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11. r_a() function
   replaced by the atomman.System.r0() method.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The minima identified by this calculation do not guarantee that the
   associated crystal structure will be stable as no relaxation is
   performed by this calculation. Upon relaxation, the atomic positions
   and box dimensions may transform the system to a different structure.
-  It is possible that the calculation may miss an existing minima for a
   crystal structure if it is outside the range of :math:`r` values
   scanned, or has :math:`b/a`, :math:`c/a` values far from the ideal.

Method and Theory
-----------------

An initial system (and corresponding unit cell system) is supplied. The
:math:`r/a` ratio is identified from the unit cell. The system is then
uniformly scaled to all :math:`r_i` values in the range to be explored
and the energy for each is evaluated using LAMMPS and “run 0” command,
i.e. no relaxations are performed.

In identifying energy minima along the curve, only the explored values
are used without interpolation. In this way, the possible energy minima
structures are identified for :math:`r_i` where
:math:`E(r_i) < E(r_{i-1})` and :math:`E(r_i) < E(r_{i+1})`.
