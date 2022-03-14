# relax_box calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The relax_box calculation style refines the lattice parameters of an orthogonal system (crystal structure) by relaxing the box dimensions towards a given pressure.  In refining the lattice parameter values, the box dimensions are allowed to relax, but the relative positions of the atoms within the box are held fixed.

This calculations provides a quick tool for obtaining lattice parameters for ideal crystal structures.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Description updated and small changes due to iprPy version.
- 2020-05-22: Version 0.10 update - potentials now loaded from database.
- 2020-09-22: Setup and parameter definition streamlined.
- 2022-03-11: Notebook updated to reflect version 0.11.  Method reworked to better treat triclinic systems.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- With this method there is no guarantee that the resulting parameters are for a stable structure.  Allowing internal relaxations may result in different values for some structures.  Additionally, some transformation paths may be restricted from occurring due to symmetry, i.e. initially cubic structures may remain cubic instead of relaxing to a non-cubic structure.
