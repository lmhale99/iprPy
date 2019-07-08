## Method and Theory

Starting with an initial unit cell, spglib is used to identify the associated primitive cell.  The primitive cell is passed to phonopy, which constructs supercell systems with small atomic displacements.  A LAMMPS calculation is performed on the displaced systems to evaluate the atomic forces on each atom without relaxing.  Phonopy then takes the measured atomic forces associated with the displacements, and computes force constants for the system.  

See phonopy documentation for more details about the package and the associated theory.