isolated_atom calculation style
===============================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The isolated_atom calculation style evaluates the base energies of all
atomic models associated with an interatomic potential. For some
potentials, the isolated energy values are necessary to properly compute
the cohesive energy of crystal structures. This also provides a simple
test whether a potential implementation is compatible with a version of
LAMMPS.

Version notes
~~~~~~~~~~~~~

-  2020-09-22: Notebook first added.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  Some potentials have two cutoffs with atomic energies outside the
   first being the “isolated” energy while outside the second have zero
   energy. The first isolated energy values for those potentials can be
   found using the diatom_scan calculation instead.

Method and Theory
-----------------

The calculation loops over all symbol models of the potential and
creates a system with a single particle inside a system with
non-periodic boundary conditions. The potential energy of each unique
isolated atom is evaluated without relaxation/integration.

The cohesive energy, :math:`E_{coh}`, of a crystal structure is given as
the per-atom potential energy of the crystal structure at equilibrium
:math:`E_{crystal}/N` relative to the potential energy of the same atoms
infinitely far apart, :math:`E_i^{\infty}`

.. math::  E_{coh} = \frac{E_{crystal} - \sum{N_i E_{i}^{\infty}}}{N},

Where the :math:`N_i` values are the number of each species :math:`i`
and :math:`\sum{N_i} = N`.

For most potentials, :math:`E_i^{\infty}=0` meaning that the measured
potential energy directly corresponds to the cohesive energy. However,
this is not the case for all potentials as some have offsets either due
to model artifacts or because it allowed for a better fitted model.
