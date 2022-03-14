# dislocation_periodic_array calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The dislocation_periodic_array calculation constructs an atomic system with a periodic array of dislocations configuration.  A single dislocation is inserted into an otherwise perfect crystal, and the system is kept periodic in the two system box directions that are within the dislocation's slip plane.  The system is then statically relaxed with the atoms at the boundary perpendicular to the slip plane held fixed.  

### Version notes

- 2019-07-30: Notebook added.
- 2020-05-22: Notebook updated for iprPy version 0.10 and tested for hcp
- 2020-09-22: Notebook updated to reflect that calculation method has changed to now use atomman.defect.Dislocation. Setup and parameter definition cleaned up and streamlined.
- 2022-03-11: Notebook updated to reflect version 0.11.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- This calculation was designed to be general enough to properly generate a dislocation for any crystal system but has not been fully tested yet for extreme cases.
