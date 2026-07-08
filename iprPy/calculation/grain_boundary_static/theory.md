## Method and Theory

### Grain boundary orientations and configurations
This method attempts to find a low energy grain boundary configuration by statically relaxing multiple grain boundary configurations.

A grain boundary orientation is defined based on a crystal unit cell and orientations of the two grains. The two grains are constructed by replicating and rotating the unit cell according to the defined orientations. However, grain orientation alone does not uniquely define a grain boundary configuration as the two grains can be rigidly shifted with respect to each other and with respect to where the grain boundary plane cleaves the grains. This calculation method explores a variety of grain boundary configurations for a given orientation by 

1. Selecting rigid body shifts from vectors in the grain boundary plane to apply to one grain with respect to the other.  These vectors are identified by finding two non-parallel lattice vectors in the grain boundary plane, then constructing a 2D map of fractional coordinates of those two vectors to explore.
2. Out-of-plane positioning is explored by deleting atoms that have neighbors in the opposite grain less than some cutoff distance. For each in-plane shift, multiple deletion cutoffs are iterated over, and the resulting configuration is only relaxed if it differs from the previous explored cutoff (i.e. additional atoms were deleted).

This sampling explores a wide range of configurations, but is not guaranteed to be complete or comprehensive. The configuration search still generates (mostly) cleanly cleaved interfaces, and the static-only relaxation does not allow for substantial atomic reconfigurations. For better configuration exploration, see the grain_boundary_grip calculation method.

### System design

All grain boundary configurations are periodic along the two shortest in-plane lattice vectors and non-periodic perpendicular to the grain boundary plane. The atoms near the non-periodic free surface are constrained: all atoms in one boundary are held fixed, and all atoms in the other boundary move as a rigid block. All atoms in between the two surface boundaries are allowed to freely relax from the energy/force minimization.  Typically, the relaxation region is 40 Angstroms wide (20 Angstroms per grain), and the boundary regions are each at least 10 Angstroms wide.