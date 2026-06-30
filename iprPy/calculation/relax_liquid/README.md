# relax_liquid calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The relax_liquid calculation style is designed to generate a liquid phase configuration for an atomic potential based on an initial configuration, target temperature and target pressure.  The calculation also computes the radial distribution function for the resulting liquid state.

### Version notes

- 2022-10-12: Calculation created
- v0.12.0: Calculation completely reworked and simplified.  Method updated to support the LAMMPS library interface.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- If starting with a crystalline configuration, be sure to use an adequately high melt temperature and number of melt steps.
- No active checks are performed by this calculation to ensure that the system is liquid. Be sure to check the final atomic configurations.
