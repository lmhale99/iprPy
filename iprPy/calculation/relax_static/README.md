# relax_static calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

## Introduction

The relax_static calculation style uses static energy/force minimizations to relax the atomic positions and box dimensions of a system to a specified pressure.

### Version notes

- This calculation style and elastic_constants_static replace the previous LAMMPS_ELASTIC calculation style.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The minimization algorithm will drive the system to a local minimum, which may not be the global minimum.  There is no guarantee that the resulting structure is dynamically stable, and it is possible that the relaxation of certain dimensions may be constrained to move together during the minimization preventing a full relaxation.
