Method and Theory
-----------------

The method starts with a bulk initial system, and relaxes the atomic
positions with a LAMMPS simulation that performs an energy/force
minimization. The cohesive energy, :math:`E_{coh}`, is taken by dividing
the system's total energy by the number of atoms in the system.

A corresponding defect system is then constructed using the
atomman.defect.point() function. The defect system is relaxed using the
same energy/force minimization as was done with the bulk system. The
formation energy of the defect, :math:`E_{ptd}^f`, is obtained as

.. math:: E_{ptd}^f = E_{ptd}^{total} - E_{coh} * n_{ptd},

where :math:`E_{ptd}^{total}` is the total potential energy of the
relaxed defect system, and :math:`n_{ptd}` is the number of atoms in the
defect system.

The atomman.defect.point() method allows for the generation of four
types of point defects:

-  **vacancy**, where an atom at a specified location is deleted.

-  **interstitial**, where an extra atom is inserted at a specified
   location (that does not correspond to an existing atom).

-  **substitutional**, where the atomic type of an atom at a specified
   location is changed.

-  **dumbbell** interstitial, where an atom at a specified location is
   replaced by a pair of atoms equidistant from the original atom's
   position.

Point defect complexes (clusters, balanced ionic defects, etc.) can also
be constructed piecewise from these basic types.

The final defect-containing system is analyzed using a few simple
metrics to determine whether or not the point defect configuration has
relaxed to a lower energy configuration:

-  **centrosummation** adds up the vector positions of atoms relative to
   the defect's position for all atoms within a specified cutoff. In
   most simple crystals, the defect positions are associated with high
   symmetry lattice sites in which the centrosummation about that point
   in the defect-free system will be zero. If the defect only
   hydrostatically displaces neighbor atoms, then the centrosummation
   should also be zero for the defect system. This is computed for all
   defect types.

.. math::  \vec{cs} = \sum_i^N{\left( \vec{r}_i - \vec{r}_{ptd} \right)} 

-  **position\_shift** is the change in position of an interstitial or
   substitutional atom following relaxation of the system. A non-zero
   value indicates that the defect atom has moved from its initially
   ideal position.

.. math::  \Delta \vec{r} = \vec{r}_{ptd} - \vec{r}_{ptd}^{0}

-  **db\_vect\_shift** compares the unit vector associated with the pair
   of atoms in a dumbbell interstitial before and after relaxation. A
   non-zero value indicates that the dumbbell has rotated from its ideal
   configuration.

.. math::  \Delta \vec{db} = \frac{\vec{r}_{db1} - \vec{r}_{db2}}{|\vec{r}_{db1} - \vec{r}_{db2}|} - \frac{\vec{r}_{db1}^0 - \vec{r}_{db2}^0}{|\vec{r}_{db1}^0 - \vec{r}_{db2}^0|}

If any of the metrics have values not close to (0,0,0), then there was
likely an atomic configuration relaxation.

The final defect system and the associated perfect base system are
retained in the calculation's archive. The calculation's record reports
the base system's cohesive energy, the point defect's formation energy,
and the values of any of the reconfiguration metrics used.
