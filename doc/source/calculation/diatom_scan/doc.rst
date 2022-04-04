diatom_scan calculation style
=============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The diatom_scan calculation style evaluates the interaction energy
between two atoms at varying distances. This provides a measure of the
isolated pair interaction of two atoms providing insights into the
strengths of the attraction/repulsion and the effective range of
interatomic spacings. This scan also gives insight into the
computational smoothness of the potential’s functional form.

Version notes
~~~~~~~~~~~~~

-  2019-07-30: Notebook added.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definition streamlined. Method and
   theory expanded.
-  2022-02-16: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  No 3+ body interactions are explored with this calculation as only
   two atoms are used.

Method and Theory
-----------------

Two atoms are placed in an otherwise empty system. The total energy of
the system is evaluated for different interatomic spacings. This
provides a means of evaluating the pair interaction component of an
interatomic potential, which is useful for a variety of reasons

-  The diatom_scan is a simple calculation that can be used to
   fingerprint a given interaction. This can be used to help determine
   if two different implementations produce the same resulting potential
   when direct comparisons of the potential parameters is not feasible.
-  For a potential to be suitable for radiation studies, the extreme
   close-range interaction energies must be prohibitively repulsive
   while not being so large that the resulting force on the atoms will
   eject them from the system during integration. The diatom_scan
   results provide a means of evaluating the close-range interactions.
-  The smoothness of the potential is also reflected in the diatom_scan
   energy results. Numerical derivatives of the measured points can
   determine the order of smoothness as well as the approximate r values
   where discontinuities occur.
-  Evaluating large separation values provides a means of identifying
   the energy of the isolated atoms, given that the separation exceeds
   the potential’s cutoff. The isolated_atom calculation is an
   alternative method for obtaining this.
