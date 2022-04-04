relax_static calculation style
==============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The relax_static calculation style uses static energy/force
minimizations to relax the atomic positions and box dimensions of a
system to a specified pressure.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definition streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The minimization algorithm will drive the system to a local minimum,
   which may not be the global minimum. There is no guarantee that the
   resulting structure is dynamically stable, and it is possible that
   the relaxation of certain dimensions may be constrained to move
   together during the minimization preventing a full relaxation.

Method and Theory
-----------------

This method uses the LAMMPS minimization plus box_relax commands to
simultaneously relax both the atomic positions and the system’s box
dimensions towards a local minimum. The LAMMPS documentation of the
box_relax command notes that the complete minimization algorithm is not
well defined which may prevent a complete relaxation during a single
run. To overcome this limitation, the calculation script continuously
restarts the minimization until the box dimensions from one run to the
next remain within a specified tolerance.
