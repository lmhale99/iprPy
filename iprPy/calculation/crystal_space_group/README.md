# crystal_space_group Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-06-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 

## Introduction

The crystal_space_group calculation characterizes a bulk atomic system (configuration) by determining its space group by evaluating symmetry elements of the box dimensions and atomic position.  This is useful for analyzing relaxed systems to determine if they have transformed to a different crystal structure.  An ideal unit cell based on the identified space group and the system's box dimensions is also generated.

__Additional dependencies__: This calculation uses the Python spglib package to perform the space group analysis.  Installing the package is required for this calculation.

__Disclaimer #1__: The results are sensitive to the symmetryprecision parameter as it defines the tolerance for identifying which atomic positions and box dimensions are symmetrically equivalent.  A small symmetryprecision value may be able to differentiate between ideal and distorted crystals, but it will cause the calculation to fail if smaller than the variability in the associated system properties.