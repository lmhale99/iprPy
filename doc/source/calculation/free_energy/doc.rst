relax_box calculation style
===========================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The free_energy calculation style uses thermodynamic integration to
evaluate the absolute Helmholtz and Gibbs free energies of a solid phase
by comparing it to a reference Einstein solid.

Version notes
~~~~~~~~~~~~~

-  2022-09-20: Calculation first added to iprPy

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The simulations used by this method are all fixed volume and
   therefore will not relax the system to a given pressure. Instead, it
   is expected that the given system is already relaxed to the target
   pressure of interest.

Method and Theory
-----------------

The calculation performs two different simulations: an nvt simulation to
estimate Einstein solid spring constants for each atom type, and
thermodynamic integrations from the selected interatomic potential to
the Einstein solid model and back. The method follows what is described
in `Freitas, Asta, de Koning, Computational Materials Science 112 (2016)
333–341 <https://doi.org/10.1016/j.commatsci.2015.10.050>`__.

The Einstein solid spring constants, :math:`k_i`, are evaluated using an
nvt simulation run and measuring the mean squared displacements,
:math:`\left<\left( \Delta r_i \right)^2\right>`, averaged for each atom
type :math:`i` and over time

.. math::  k_i = \frac{3 k_B T}{\left<\left( \Delta r_i \right)^2\right>} 

For the integration, TBD…
