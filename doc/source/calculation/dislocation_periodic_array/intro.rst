Introduction
============

The dislocation_periodic_array calculation constructs an atomic system
with a periodic array of dislocations configuration. A single
dislocation is inserted into an otherwise perfect crystal, and the
system is kept periodic in the two system box directions that are within
the dislocation’s slip plane. The system is then statically relaxed with
the atoms at the boundary perpendicular to the slip plane held fixed.
The generated system can then be used by the other
"dislocation_periodic_array_*" calculations for examining the slip
response of a dislocation to applied stresses or strain rates.

Version notes
~~~~~~~~~~~~~

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  This calculation was designed to be general enough to properly
   generate a dislocation for any crystal system, but has so far only
   been tested with cubic systems. The resulting system should be
   carefully examined if the base system in which the dislocation is
   inserted is not orthorhombic. In particular, the method may need
   adjusting if the :math:`\vec{c}` box vector has a large :math:`y`
   component.
