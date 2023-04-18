bond_angle_scan calculation style
=================================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The bond_angle_scan calculation style evaluates the interaction energy
between three atoms at varying distances and angles. This provides a
means of characterizing the three-body interactions of a given
potential. These interactions can provide insight into the bonding
predictions for a potential as well as a means of fingerprinting the
potentials.

Version notes
~~~~~~~~~~~~~

-  2021-04-XX: Calculation added

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__

Method and Theory
-----------------

Three atoms are placed in an otherwise empty system. The relative
positions of the atoms are determined by the following three coordinates

-  r_ij is the radial distance between atoms i and j,
-  r_ik is the radial distance between atoms i and k, and
-  theta_ijk is the angle formed between the i-j and i-k vectors.

Based on these three bond coordinates, the full positions of the three
atoms in the system are determined as follows

-  Atom i is positioned at the system’s origin, [0, 0, 0]
-  Atom j is placed r_ij away from atom i along the x coordinate, [r_ij,
   0.0, 0.0]
-  Atom k is placed in the xy plane based on r_ik and theta_ijk, [r_ik
   cos(theta_ijk), r_ik sin(theta_ijk), 0.0]

Values of r_ij, r_ik and theta_ijk are iterated over. The potential
energy of the three atoms is evaluated for each configuration
corresponding to the different coordinate sets.
