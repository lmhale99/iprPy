# relaxed_crystal Record style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2019-04-09

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The relaxed_crystal Record style defines a crystal structure that is known to be unique and stable for a specific interatomic potential.  These records are generated either by

- Analysis of the calculation_crystal_space_group records to identify all unique crystal structures that did not transform following relaxation.

- Manual definitions for known "trouble" crystal structures.  In particular, some older EAM potentials are known to have functional discontinuities exactly corresponding to the ideal fcc lattice.  Properly computing certain static properties, such as elastic constants, requires defining crystals with slightly different lattice constants.