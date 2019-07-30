Introduction
============

The relaxed_crystal record style defines a crystal structure that is
known to be unique and stable for a specific interatomic potential.
These records are generated either by

-  Analysis of the calculation_crystal_space_group records to identify
   all unique crystal structures that did not transform following
   relaxation.
-  Manual definitions for known “trouble” crystal structures. In
   particular, some older EAM potentials are known to have functional
   discontinuities exactly corresponding to the ideal fcc lattice.
   Properly computing certain static properties, such as elastic
   constants, requires defining crystals with slightly different lattice
   constants.

Version notes
~~~~~~~~~~~~~

-  iprPy version 0.9: the contained atomic system configuration was
   updated to the new atomman.System model format.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
