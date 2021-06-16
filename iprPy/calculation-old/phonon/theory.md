## Method and Theory

Starting with an initial system, [spglib](https://atztogo.github.io/spglib/python-spglib.html) is used to identify the associated primitive unit cell.  The primitive cell is passed to [phonopy](https://atztogo.github.io/phonopy/), which constructs super cell systems with small atomic displacements.  A LAMMPS calculation is performed on the displaced systems to evaluate the atomic forces on each atom without relaxing.  The measured atomic forces are then passed back to phonopy, which computes force constants for the system.  Plots are then created for the band structure, density of states, and other thermal properties.

See [phonopy](https://atztogo.github.io/phonopy/) documentation for more details about the package and the associated theory.
