# relax_static Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-06-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 

## Introduction

The relax_static calculation uses static energy/force minimizations to relax the atomic positions and box dimensions of a system to a specified pressure.

__Version notes__: This calculation and elastic_constants_static replace the previous LAMMPS_ELASTIC calculation style.

__Disclaimer #1__: The minimization algorithm will drive the system to a local minimum, which may not be the global minimum.  There is no guarantee that the resulting structure is dynamically stable, and it is possible that the relaxation of certain dimensions may be constrained to move together during the minimization preventing a full relaxation.