# surface_energy_static calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The surface_energy_static calculation style evaluates the formation energy for a free surface by slicing an atomic system along a specific plane.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Description updated and small changes due to iprPy version.
- v0.10.0: Version 0.10 update - potentials now loaded from database.
- 2020-09-22: Calculation updated to use atomman.defect.FreeSurface class. Setup and parameter definition streamlined.
- v0.11.0: Notebook updated to reflect version 0.11.
- v0.12.0: Method updated to support the LAMMPS library interface.
  
### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- Other atomic configurations at the free surface for certain planar cuts may have lower energies.  The atomic relaxation will find a local minimum, which may not be the global minimum.  Additionally, the material cut is planar perfect and therefore does not explore the effects of atomic roughness.
