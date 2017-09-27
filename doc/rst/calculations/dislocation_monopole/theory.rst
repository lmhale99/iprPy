
Method and Theory
*****************

First, an initial system is generated. This is accomplished by

1. Starting with a unit cell system.

2. Generating a transformed system by rotating the unit cell such that
   the new system's box vectors correspond to crystallographic
   directions, and filled in with atoms to remain a perfect bulk cell
   when the three boundaries are periodic.

3. All atoms are shifted by a fractional amount of the box vectors if
   needed.

4. A supercell system is constructed by combining multiple replicas of
   the transformed system.

The Stroh method is used to compute the Eshelby solution for an
anisotropic straight dislocation. This is done using the
atomman.defect.Stroh class. The solution is computed for a dislocation
parallel to the initial system's z-axis using the bulk elastic
constants tensor for the system, C_{ij}, and the dislocation's Burgers
vector, b_i.

A dislocation monopole system is constructed with dislocation line
positioned along the z-axis, i.e. xy coordinates = (0,0). For every
atom in the initial system, the Stroh displacement is computed based
on their xy coordinates and the Stroh solution. The dislocation system
is then created by shifting the atomic positions of the initial system
by the Stroh displacements.

The boundary conditions of the dislocation monopole system are handled
as such:

1. The box dimension parallel to the z-axis is periodic, and the other
   two box directions are non-periodic.

2. The system is divided into active and fixed regions.

1. The fixed region consists of atoms near the x and y boundaries and
   should always be of a thickness such that atoms in the active
   region do not interact with the free surfaces.

2. The active region is centered around the dislocation line, and has
   a cross-sectional area that is either circular or rectangular.

1. Atoms in the fixed region are identified by altering their integer
   atomic types.

Finally, a LAMMPS simulation is performed using the dislocation
monopole system. In the simulation, the atoms in the active region are
allowed to relax either with nvt integration followed by an
energy/force minimization, or with just an energy/force minimization.
The atoms in the fixed region are not allowed to relax and remain
fixed (at the elastic solution). Upon completion, the relaxed
dislocation system and parameters from the Stroh solution are
retained.
