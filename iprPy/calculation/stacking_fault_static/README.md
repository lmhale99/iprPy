# stacking_fault_static calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The stacking_fault_static calculation style evaluates the energy of a single generalized stacking fault shift along a specified crystallographic plane.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Description updated and small changes due to iprPy version.
- 2020-05-22: Version 0.10 update - potentials now loaded from database.
- 2020-09-22: Calculation updated to use atomman.defect.StackingFault class. Setup and parameter definition streamlined.
- 2022-03-11: Notebook updated to reflect version 0.11.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The system's dimension perpendicular to the fault plane should be large to minimize the interaction of the free surface and the stacking fault.
