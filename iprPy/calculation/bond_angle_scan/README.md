# bond_angle_scan calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The bond_angle_scan calculation style evaluates the interaction energy between three atoms at varying distances and angles.  This provides a means of characterizing the three-body interactions of a given potential.  These interactions can provide insight into the bonding predictions for a potential as well as a means of fingerprinting the potentials.

### Version notes

- 2021-04-30: Calculation added.
- 2026-06-25: Method updated to support the LAMMPS library interface. Runs are also faster as a single LAMMPS instance is used.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
