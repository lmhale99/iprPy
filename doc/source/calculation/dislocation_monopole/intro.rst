Introduction
============

The dislocation_monopole calculation style calculation inserts a
dislocation monopole into an atomic system using the anisotropic
elasticity solution for a perfectly straight dislocation. The system is
divided into two regions: a boundary region at the system’s edges
perpendicular to the dislocation line, and an active region around the
dislocation. After inserting the dislocation, the atoms within the
active region of the system are relaxed while the positions of the atoms
in the boundary region are held fixed at the elasticity solution. The
relaxed dislocation system and corresponding dislocation-free base
systems are retained in the calculation’s archived record. Various
properties associated with the dislocation’s elasticity solution are
recorded in the calculation’s results record.

Version notes
~~~~~~~~~~~~~

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  This calculation method holds the boundary atoms fixed during the
   relaxation process which results in a mismatch stress at the border
   between the active and fixed regions that interacts with the
   dislocation. Increasing the distance between the dislocation and the
   boundary region, i.e. increasing the system size, will reduce the
   influence of the mismatch stresses.
-  The boundary atoms are fixed at the elasticity solution, which
   assumes the dislocation to be compact (not spread out, dissociated
   into partials) and to remain at the center of the system. An
   alternate simulation design or boundary region method should be used
   if you want accurate simulations of dislocations with wide cores
   and/or in which the dislocation moves long distances.
-  The calculation allows for the system to be relaxed either using only
   static energy/force minimizations or with molecular dynamic steps
   followed by a minimization. Only performing a static relaxation is
   considerably faster than performing a dynamic relaxation, but the
   dynamic relaxation is more likely to result in a better final
   dislocation structure.
