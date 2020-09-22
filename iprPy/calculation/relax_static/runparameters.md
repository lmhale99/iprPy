### Run parameters

Provides parameters specific to the calculation at hand.

- __pressure_xx, pressure_yy, pressure_zz, pressure_xy, pressure_xz, pressure_yz__: specifies the pressures to relax the box to. Default values are '0 GPa' for all.
- __displacementkick__: a multiplier for applying a small random displacement to all atoms prior to relaxing.  Giving this can break the system's initial symmetry to avoid the relaxation calculation being constrained by too perfect of symmetry.  Default value is '0.0 angstrom', i.e. no kick.
- __maxcycles__: specifies the maximum number of minimization runs (cycles) to perform.  Specifying '1' means that only one minimization is performed and no check is made for convergence.  Default value is '100'.
- __cycletolerance__: specifies the tolerance to use in determining if the lattice constants have converged between two minimization runs (cycles).  Default value is '1e-10 angstrom'.
