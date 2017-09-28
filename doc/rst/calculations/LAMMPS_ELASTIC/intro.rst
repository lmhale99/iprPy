Introduction
============

The LAMMPS\_ELASTIC calculation refines the lattice parameters of a
structure and computes the structure's elastic constants,
:math:`C_{ij}`, using the ELASTIC script distributed with the LAMMPS MD
software. Energy minimization is used to relax the system's box
dimensions and local atomic configurations. Once the system converges,
the elastic constants are estimated by applying small strains. For
better convergence of the box dimensions, the calculation script runs
the ELASTIC script multiple times until the box dimensions stop
changing.

This calculation provides a quick tool for obtaining both the lattice
and elastic constants for a given structure.

**Disclaimer #1**: With this method there is no guarantee that the
resulting parameters are for a stable structure. The minimization
algorithm can have trouble relaxing box dimensions if the initial guess
is far from the equilibrium dimensions. Additionally, some
transformation paths may be restricted from occurring due to symmetry,
i.e. initially cubic structures may remain cubic instead of relaxing to
a non-cubic structure.

**Disclaimer #2**: The elastic constants are estimated using small
strains. Depending on the potential, the values for the elastic
constants may vary with the size of the strain. This can come about
either if the strain exceeds the linear elastic regime, or if the
potential energy is not continuous to the fourth derivative.
