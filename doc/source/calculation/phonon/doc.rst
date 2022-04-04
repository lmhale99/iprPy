phonon calculation style
========================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The phonon calculation style applies small atomic displacements to a
unit cell system and evaluates the forces on the atoms to evaluate
phonon-based properties.

Version notes
~~~~~~~~~~~~~

-  2020-12-21: Script extended to include quasiharmonic calculations.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

-  `spglib <https://atztogo.github.io/spglib/python-spglib.html>`__
-  `phonopy <https://atztogo.github.io/phonopy/>`__
-  `seekpath <https://pypi.org/project/seekpath/>`__

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__

Method and Theory
-----------------

Starting with an initial system,
`spglib <https://atztogo.github.io/spglib/python-spglib.html>`__ is used
to identify the associated primitive unit cell. The primitive cell is
passed to `phonopy <https://atztogo.github.io/phonopy/>`__, which
constructs super cell systems with small atomic displacements. A LAMMPS
calculation is performed on the displaced systems to evaluate the atomic
forces on each atom without relaxing. The measured atomic forces are
then passed back to phonopy, which computes force constants for the
system. Plots are then created for the band structure, density of
states, and other thermal properties.

See `phonopy <https://atztogo.github.io/phonopy/>`__ documentation for
more details about the package and the associated theory.
