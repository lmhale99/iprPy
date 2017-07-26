## Method and Theory

A perfect crystal system is constructed in which two of the system's boundary conditions are periodic and the third is non-periodic (defined by the calculation using cutboxvector). To ensure that the shift is properly handled across the periodic directions, the box vector, ``$\vec{a}$``, ``$\vec{b}$``, or ``$\vec{c}$``, assigned to cutboxvector must have a Cartesian ``$x$``, ``$y$``, or ``$z$`` component that the other two box vectors do not. If true, then the non-periodic boundary will be perpendicular to that Cartesian axis, and the periodic box vectors will be parallel to the cut plane.

For LAMMPS compatible systems, the above rule places the following limitations on allowed systems:

- cutboxvector = 'c': all systems allowed.

- cutboxvector = 'b': the system's yz tilt must be zero.

- cutboxvector = 'a': the system's xy and xz tilts must be zero.

Once the system is constructed, a LAMMPS simulation performs an energy/force minimization and evaluates the system's total potential energy, ``$E^{total}(\vec{0})$``. 

A mathematical fault plane is defined in the middle of the system parallel to the free surface plane created by the non-periodic boundary. All atoms on one side of the fault plane are then shifted by a vector contained within the fault plane, ``$\vec{s}$``. After shifting, the system is subjected to an energy/force minimization where all atoms are only allowed to relax normal to the plane, and the system's total potential energy, ``$E^{total}(\vec{s})$``, is measured.

For the stacking_fault calculation, only one shift is applied. For the stacking_fault_multi calculation, a regular array of points is constructed based on two non-parallel vectors, ``$\vec{s_1}$`` and ``$\vec{s_2}$``, that are in the fault plane. These two shift vectors should each correspond to a full periodic shift of the plane such that applying the full shift results in a system equivalent to the unshifted configuration. The evaluation grid is then constructed by taking fractional steps along both shift vectors.

The generalized stacking fault energy, ``$E_{GSF}(\vec{s})$``, is then measured as

$$ E_{GSF}(\vec{s}) = \frac{E^{total}(\vec{s}) - E^{total}(\vec{0})}{A_{fault}},$$

where ``$A_{fault}$`` is the area of the fault plane.

Additionally, the relaxation normal to the glide plane, ``$\Delta\delta_{GSF}$``,  is characterized by finding the change in the centers of mass of the shifted and unshifted regions perpendicular to the glide plane.