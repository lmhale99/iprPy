# dislocation_dipole calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The dislocation_dipole calculation style calculation creates a small-cell dislocation dipole configuration consisting of two dislocations of opposite sign.  This type of cell allows for all three dimensions to be periodic and stabilizes the dislocation core positions by applying a counteracting strain.  The resulting configuration is consistent with a periodic 2D array of dislocations with alternating burgers vector signs.

### Version notes

- 2024-12-19: Calculation added

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- This calculation is best used with dislocation cores that remain compact and do not split or spread along the slip plane as the cores should not overlap or interfere with each other.
- The allowed size dimensions is a little unintuitive due to being dependent on the crystal symmetry. Trying guess values on a test system is usually adequate for finding good values.
- The calculation allows for the system to be relaxed either using only static energy/force minimizations or with molecular dynamic steps followed by a minimization.  Only performing a static relaxation is considerably faster than performing a dynamic relaxation, but the dynamic relaxation is more likely to result in a better final dislocation structure. If a dynamic relaxation is performed, the temperature should be kept low to prevent the dislocations from slipping and potentially annihilating each other.
