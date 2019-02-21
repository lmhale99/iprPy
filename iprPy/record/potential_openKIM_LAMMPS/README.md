# potential_LAMMPS Record style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2019-02-08

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The potential_openKIM_LAMMPS Record style is for collecting the parameters associated with a LAMMPS implemented interatomic potential.  It can be read in and interpreted using the atomman.lammps.Potential class.

The potential_*LAMMPS record styles are all identical and are only separated based on the content source:

- **potential_LAMMPS** represents the potential implementations that are hosted on the NIST Interatomic Potentials Repository.

- **potential_openKIM_LAMMPS** represents the potential implementations that are integrated into the openKIM framework.

- **potential_users_LAMMPS** represents the potential implementations that are defined and added by users.  Unlike the other two, the associated library folder for these potentials is not tracked by git.