Introduction
============

The dislocation record style is used for representing a specific
dislocation as stored in the iprPy reference library. Each record is
associated with a specific dislocation type, and contains
characterization metadata and parameters associated with generating the
defect in a simulation.

Version notes
~~~~~~~~~~~~~

-  iprPy version 0.9: the style was renamed from dislocation_monopole as
   the parameters can be used to generate dislocations in other system
   configurations.
-  iprPy version 0.8: The orientations of the pre-defined dislocation
   configurations in the dislocation_monopole records have been changed
   such that the dislocation line is now parallel to the x-axis rather
   than the z-axis. This orientation is more compatible to constructing
   dislocation systems for any crystal system.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
