# crystal_space_group calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The crystal_space_group calculation style characterizes a bulk atomic system (configuration) by determining its space group by evaluating symmetry elements of the box dimensions and atomic position.  This is useful for analyzing relaxed systems to determine if they have transformed to a different crystal structure.  An ideal unit cell based on the identified space group and the system's box dimensions is also generated.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Function slightly updated
- 2020-09-22: Setup and parameter definition streamlined. Method and theory expanded.
- 2022-03-11: Notebook updated to reflect version 0.11.

### Additional dependencies

- [spglib](https://atztogo.github.io/spglib/python-spglib.html)

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

- The results are sensitive to the symmetryprecision parameter as it defines the tolerance for identifying which atomic positions and box dimensions are symmetrically equivalent.  A small symmetryprecision value may be able to differentiate between ideal and distorted crystals, but it will cause the calculation to fail if smaller than the variability in the associated system properties.
