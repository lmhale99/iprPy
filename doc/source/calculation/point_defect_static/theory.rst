Method and Theory
-----------------

The method starts with a bulk initial system, and relaxes the atomic
positions with a LAMMPS simulation that performs an energy/force
minimization. The cohesive energy, :math:`E_{coh}`, is taken by dividing
the system’s total energy by the number of atoms in the system.

A corresponding defect system is then constructed using the
atomman.defect.point() function. The defect system is relaxed using the
same energy/force minimization as was done with the bulk system. The
formation energy of the defect, :math:`E_{f}^{ptd}`, is obtained as

.. math:: E_{f}^{ptd} = E_{total}^{ptd} - E_{coh} * N^{ptd},

where :math:`E_{total}^{ptd}` is the total potential energy of the
relaxed defect system, and :math:`N^{ptd}` is the number of atoms in the
defect system.

The elastic dipole tensor, :math:`P_{ij}`, is also estimated for the
point defect. :math:`P_{ij}` is a symmetric second rank tensor that
characterizes the elastic nature of the defect. Here, :math:`P_{ij}` is
estimated using [`1 <https://doi.org/10.1080/01418618108239410>`__,
`2 <https://doi.org/10.1080/01418618308244326>`__]

.. math::  P_{ij} = -V \langle \sigma_{ij} \rangle,

where :math:`V` is the system cell volume and
:math:`\langle \sigma_{ij} \rangle` is the residual stress on the system
due to the defect, which is computed using the measured cell stresses
(pressures) of the defect-free system, :math:`\sigma_{ij}^{0}`, and the
defect-containing system, :math:`\sigma_{ij}^{ptd}`

.. math:: \langle \sigma_{ij} \rangle = \sigma_{ij}^{ptd} - \sigma_{ij}^{0}.

The atomman.defect.point() method allows for the generation of four
types of point defects:

-  **vacancy**, where an atom at a specified location is deleted.

-  **interstitial**, where an extra atom is inserted at a specified
   location (that does not correspond to an existing atom).

-  **substitutional**, where the atomic type of an atom at a specified
   location is changed.

-  **dumbbell** interstitial, where an atom at a specified location is
   replaced by a pair of atoms equidistant from the original atom’s
   position.

Point defect complexes (clusters, balanced ionic defects, etc.) can also
be constructed piecewise from these basic types.

The final defect-containing system is analyzed using a few simple
metrics to determine whether or not the point defect configuration has
relaxed to a lower energy configuration:

-  **centrosummation** adds up the vector positions of atoms relative to
   the defect’s position for all atoms within a specified cutoff. In
   most simple crystals, the defect positions are associated with high
   symmetry lattice sites in which the centrosummation about that point
   in the defect-free system will be zero. If the defect only
   hydrostatically displaces neighbor atoms, then the centrosummation
   should also be zero for the defect system. This is computed for all
   defect types.

.. math::  \vec{cs} = \sum_i^N{\left( \vec{r}_i - \vec{r}_{ptd} \right)} 

-  **position_shift** is the change in position of an interstitial or
   substitutional atom following relaxation of the system. A non-zero
   value indicates that the defect atom has moved from its initially
   ideal position.

.. math::  \Delta \vec{r} = \vec{r}_{ptd} - \vec{r}_{ptd}^{0}

-  **db_vect_shift** compares the unit vector associated with the pair
   of atoms in a dumbbell interstitial before and after relaxation. A
   non-zero value indicates that the dumbbell has rotated from its ideal
   configuration.

.. math::  \Delta \vec{db} = \frac{\vec{r}_{db1} - \vec{r}_{db2}}{|\vec{r}_{db1} - \vec{r}_{db2}|} - \frac{\vec{r}_{db1}^0 - \vec{r}_{db2}^0}{|\vec{r}_{db1}^0 - \vec{r}_{db2}^0|}

If any of the metrics have values not close to (0,0,0), then there was
likely an atomic configuration relaxation.

The final defect system and the associated perfect base system are
retained in the calculation’s archive. The calculation’s record reports
the base system’s cohesive energy, the point defect’s formation energy,
and the values of any of the reconfiguration metrics used.
