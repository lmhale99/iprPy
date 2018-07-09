Method and Theory
-----------------

This method uses the LAMMPS minimization plus box\_relax commands to
simultaneously relax both the atomic positions and the system's box
dimensions towards a local minimum. The LAMMPS documentation of the
box\_relax command notes that the complete minimization algorithm is not
well defined which may prevent a complete relaxation during a single
run. To overcome this limitation, the calculation script continuously
restarts the minimization until the box dimensions from one run to the
next remain within a specified tolerance.
