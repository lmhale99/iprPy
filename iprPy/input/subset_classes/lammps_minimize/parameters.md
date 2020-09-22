### LAMMPS minimization parameters

Specifies the run parameters associated with an energy/force minimization in LAMMPS.

- __energytolerance__: specifies the energy tolerance to use for the minimization.  This value is unitless and corresponds to the etol term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 0.
- __forcetolerance__: specifies the force tolerance to use for the minimization.  This value is in force units and corresponds to the ftol term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is '1.0e-10 eV/angstrom'.
- __maxiterations__: specifies the maximum number of iterations to use for the minimization. This value corresponds to the maxiter term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 1000.
- __maxevaluations__: specifies the maximum number of iterations to use for the minimization. This value corresponds to the maxeval term for the [LAMMPS minimize command.](http://lammps.sandia.gov/doc/minimize.html)  Default value is 10000.
- __maxatommotion__: specifies the maximum distance that any atom can move during a minimization iteration. This value is in units length and corresponds to the dmax term for the [LAMMPS min_modify command.](http://lammps.sandia.gov/doc/min_modify.html)  Default value is '0.01 angstrom'.
