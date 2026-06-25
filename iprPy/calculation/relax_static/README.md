# relax_static calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The relax_static calculation style uses static energy/force minimizations to relax the atomic positions and box dimensions of a system to a specified pressure.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Description updated and small changes due to iprPy version.
- v0.10.0: Version 0.10 update - potentials now loaded from database.
- 2020-09-22: Setup and parameter definition streamlined.
- v0.11.0: Notebook updated to reflect version 0.11.
- v0.11.1: raise_at_maxcycles parameter added that when set to
  False will allow calculations to finish without error if maxcycles is reached.
- v0.12.0: Method updated to support the LAMMPS library interface.
  
### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The minimization algorithm will drive the system to a local minimum, which may not be the global minimum.  There is no guarantee that the resulting structure is dynamically stable, and it is possible that the relaxation of certain dimensions may be constrained to move together during the minimization preventing a full relaxation.
