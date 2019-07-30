Introduction
============

The point_defect_static calculation style computes the formation energy
of a point defect by comparing the energies of a system before and after
a point defect is inserted. The resulting defect system is analyzed
using a few different metrics to help characterize if the defect
reconfigures to a different structure upon relaxation.

Version notes
~~~~~~~~~~~~~

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The computed values of the point defect formation energies and
   elastic dipole tensors are sensitive to the size of the system.
   Larger systems minimize the interaction between the defects, and the
   affect that the defects have on the system’s pressure. Infinite
   system formation energies can be estimated by measuring the formation
   energy for multiple system sizes, and extrapolating to 1/natoms = 0.
-  Because only a static relaxation is performed, the final
   configuration might not be the true stable configuration.
   Additionally, the stable configuration may not correspond to any of
   the standard configurations characterized by the point-defect records
   in the iprPy/library. Running multiple configurations increases the
   likelihood of finding the true stable state, but it does not
   guarantee it. Alternatively, a dynamic simulation or a genetic
   algorithm may be more thorough.
-  The metrics used to identify reconfigurations are not guaranteed to
   work for all crystals and defects. Most notably, the metrics assume
   that the defect’s position coincides with a high symmetry site in the
   lattice.
-  The current version assumes that the initial defect-free base system
   is an elemental crystal structure. The formation energy expression
   needs to be updated to handle multi-component crystals.
