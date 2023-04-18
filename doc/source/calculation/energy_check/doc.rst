energy_check calculation style
==============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Idea suggested by Udo v. Toussaint (Max-Planck-Institute
f. Plasmaphysics)

Introduction
------------

The energy_check calculation style provides a quick check if the energy
of an atomic configuration matches with an expected one.

Version notes
~~~~~~~~~~~~~

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__

-  Small variations in the energy are to be expected due to numerical
   precisions.

Method and Theory
-----------------

The calculation performs a quick run 0 (no relaxation) energy
calculation on a given atomic configuration using a given potential and
compares the computed potential energy versus an expected energy value.
