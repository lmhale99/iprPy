Introduction
============

The crystal\_space\_group calculation characterizes a bulk atomic system
(configuration) by determining its space group by evaluating symmetry
elements of the box dimensions and atomic position. This is useful for
analyzing relaxed systems to determine if they have transformed to a
different crystal structure. An ideal unit cell based on the identified
space group and the system's box dimensions is also generated.

**Additional dependencies**: This calculation uses the Python spglib
package to perform the space group analysis. Installing the package is
required for this calculation.

**Disclaimer #1**: The results are sensitive to the symmetryprecision
parameter as it defines the tolerance for identifying which atomic
positions and box dimensions are symmetrically equivalent. A small
symmetryprecision value may be able to differentiate between ideal and
distorted crystals, but it will cause the calculation to fail if smaller
than the variability in the associated system properties.
