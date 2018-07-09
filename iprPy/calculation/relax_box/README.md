# relax_box Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-06-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
## Introduction

The relax_box calculation refines the lattice parameters of an orthogonal system (crystal structure) by relaxing the box dimensions towards a given pressure.  In refining the lattice parameter values, the box dimensions are allowed to relax, but the relative positions of the atoms within the box are held fixed.

This calculations provides a quick tool for obtaining lattice parameters for ideal crystal structures.

__Version notes__: This was previously called the refine_structure calculation and was renamed for consistency with other calculations.  Additionally, reporting of the elastic constants is removed as their values may be incorrect for some crystal structures.

__Disclaimer #1__: With this method there is no guarantee that the resulting parameters are for a stable structure.  Allowing internal relaxations may result in different values for some structures.  Additionally, some transformation paths may be restricted from occurring due to symmetry, i.e. initially cubic structures may remain cubic instead of relaxing to a non-cubic structure.