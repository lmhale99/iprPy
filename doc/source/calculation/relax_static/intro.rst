Introduction
============

The relax\_static calculation uses static energy/force minimizations to
relax the atomic positions and box dimensions of a system to a specified
pressure.

**Version notes**: This calculation and elastic\_constants\_static
replace the previous LAMMPS\_ELASTIC calculation style.

**Disclaimer #1**: The minimization algorithm will drive the system to a
local minimum, which may not be the global minimum. There is no
guarantee that the resulting structure is dynamically stable, and it is
possible that the relaxation of certain dimensions may be constrained to
move together during the minimization preventing a full relaxation.
