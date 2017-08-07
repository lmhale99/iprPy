## Method and Theory

An initial system is supplied, and a LAMMPS simulation performs an energy/force minimization on the system and estimates the total potential energy of the perfect bulk system, $E_{bulk}^{total}$. A corresponding defect system is constructed by changing one of the three boundary conditions from periodic to non-periodic. This effectively slices the system along the boundary plane creating two free surfaces, each with surface area $A_{surface}$. The defect system is then relaxed with an energy/force minimization and the total potential energy of the defect system, $E_{surface}^{total}$, is measured. The formation energy of the free surface, $E_{surface}^f$, is computed in units of energy over area as

$$E_{surface}^f = \frac{E_{surface}^{total} - E_{bulk}^{total}} {2 A_{surface}}.$$

The particular free surface created depends on the system's orientation, initial atomic shift, and the specific system box vector ($a$, $b$, or $c$) along which the cut is made. Care should be made such that the atomic shift avoids placing an atomic plane directly at the cut plane.