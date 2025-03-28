## Method and Theory

### Dislocation construction

The construction of dislocations using the Volterra dislocation solutions corresponds to what is described in the dislocation_monopole documentation.  Constructing a dipole configuration builds upon this by:

1. Obtaining two solutions of the Volterra dislocation, one with a positive Burgers vector and one with a negative Burgers vector that are located equidistant between replicas along the slip plane.  The displacement fields for the two solutions are added together to produce an approximate displacement field for the dipole system.
2. The approximate dipole solution is used to compute the displacement that should act on the cell from a number of neighboring periodic cells.  These neighbor cell solutions are added to the approximate solution.
3. A linear displacement is added on to correct for the error in using a limited number of periodic cells in step 2.  This displacement is identified as ensuring atomic compatibility across the periodic boundaries.
4. A strain is applied to the system to counteract the elastic attraction between the two dislocations.

