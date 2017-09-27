
Introduction
************

The point_defect_static calculation computes the formation energy of a
point defect by comparing the energies of a system before and after a
point defect is inserted. The resulting defect system is analyzed
using a few different metrics to help characterize if the defect
reconfigures to a different structure upon relaxation.

**Disclaimer #1**: Point defect formation values are sensitive to the
size of the system. Larger systems minimize the interaction between
the defects, and the affect that the defects have on the system's
pressure. Infinite system formation energies can be estimated by
measuring the formation energy for multiple system sizes, and
extrapolating to 1/natoms = 0.

**Disclaimer #2**: Because only a static relaxation is performed, the
final configuration might not be the true stable configuration.
Additionally, the stable configuration may not correspond to any of
the standard configurations characterized by the point-defect records
in the iprPy/library. Running multiple configurations increases the
likelihood of finding the true stable state, but it does not guarantee
it. Alternatively, a dynamic simulation or a genetic algorithm may be
more thorough.

**Disclaimer #3**: The reconfiguration metrics should be considered as
guidelines, not as absolute. Because most standard sites for point
defects are positions of high-symmetry, they will likely work well for
most simple cases.

**Disclaimer #4**: The current version assumes that the initial
defect-free base system is an elemental crystal structure. The
formation energy expression will have to updated to handle
multi-component crystals.
