Introduction
============

The isolated_atom calculation style evaluates the base energies of all
atomic models associated with an interatomic potential. For some
potentials, the isolated energy values are necessary to properly compute
the cohesive energy of crystal structures. This also provides a simple
test whether a potential implementation is compatible with a version of
LAMMPS.

Version notes
~~~~~~~~~~~~~

-  2020-09-22: Notebook first added.

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
