## Method and Theory

### GRIP grain boundary relaxations

This method uses the grand canonical interface predictor (GRIP) algorithm to construct a grain boundary configuration for a given crystal and orientation, and then relaxes the configuration. To explore a wide range of configurations, the alignment of the two grains, numbers and positions of atoms at the grain boundary, and relaxation settings are all randomly selected. Repeatedly running the calculation allows for many relaxations to be sampled which can reveal new low energy configurations, and the dependence of the grain boundary configuration on the number of vacancies/interstitials at the boundary.

See the atomman.defect.GRIP documentation for more details on the random values...

### System design

All grain boundary configurations are periodic along the two shortest in-plane lattice vectors and non-periodic perpendicular to the grain boundary plane. The atoms near the non-periodic free surface are constrained: all atoms in one boundary are held fixed, and all atoms in the other boundary move as a rigid block. The widths of the relaxation and boundary regions depend on the relaxation stage. For the MD stage, only the atoms closest to the grain boundary (typically 10 Angstroms into each grain) are allowed to relax, while the remaining atoms are treated as the surface boundaries.  For the energy/force minimization stage, the active region is doubled (40 Angstroms total, 20 in each grain). The total width of the system is selected to be such that the surface boundary regions are always at least 10 Angstroms thick, thus the total width is > 60 Angstroms, 30 Angstroms per grain.
