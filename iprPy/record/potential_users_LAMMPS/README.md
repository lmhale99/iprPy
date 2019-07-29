# potential_LAMMPS record style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

## Introduction

The potential_users_LAMMPS record style is for collecting the parameters associated with a LAMMPS implemented interatomic potential.  It can be read in and interpreted using the atomman.lammps.Potential class.

The potential_*LAMMPS record styles are all identical and are separated based on the content source and git tracking:

- **potential_LAMMPS** represents the potential implementations that are hosted on the NIST Interatomic Potentials Repository.

- **potential_openKIM_LAMMPS** represents the potential implementations that are integrated into the openKIM framework.

- **potential_users_LAMMPS** represents the potential implementations that are defined and added by users.  Unlike the other two, the associated library folder for these potentials is not tracked by git.

### Version notes

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
