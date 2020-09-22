### Run parameters

Provides parameters specific to the calculation at hand.

- __symmetryprecision__: a precision tolerance used for the atomic positions and box dimensions for determining symmetry elements.  Default value is '0.01 angstrom'.
- __primitivecell__: a boolean flag indicating if the returned unit cell is to be primitive (True) or conventional (False).  Default value is False.
- __idealcell__: a boolean flag indicating if the box dimensions and atomic positions are to be idealized based on the space group (True) or averaged based on their actual values (False).  Default value is True.
