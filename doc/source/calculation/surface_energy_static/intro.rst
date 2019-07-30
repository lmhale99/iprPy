Introduction
============

The surface_energy_static calculation style evaluates the formation
energy for a free surface by slicing an atomic system along a specific
plane.

Version notes
~~~~~~~~~~~~~

-  This was previously called the surface_energy calculation style and
   was renamed for consistency.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  Other atomic configurations at the free surface for certain planar
   cuts may have lower energies. The atomic relaxation will find a local
   minimum, which may not be the global minimum. Additionally, the
   material cut is planar perfect and therefore does not explore the
   effects of atomic roughness.
