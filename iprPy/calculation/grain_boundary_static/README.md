# grain_boundary_static calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The grain_boundary_static calculation style constructs and evaluates grain boundary structures and energies for a given grain boundary orientation by performing only static energy/force relaxations.  Each calculation performs multiple grain boundary structure relaxations in a search for the in- and out-of plane shifts that produce the lowest energy structure. 

### Version notes

- v0.??.?: Calculation method created by combining and generalizing the previous grain_boundary_search and grain_boundary_bcc methods.
- v0.11.?: Calculation method updated to be consistent with the new grain_boundary_grip method by using small non-periodic atomic configurations.
- v0.12.0: Method updated to support the LAMMPS library interface.
  
### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

