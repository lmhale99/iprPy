relax_box calculation style
===========================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The relax_box calculation style refines the lattice parameters of an
orthogonal system (crystal structure) by relaxing the box dimensions
towards a given pressure. In refining the lattice parameter values, the
box dimensions are allowed to relax, but the relative positions of the
atoms within the box are held fixed.

This calculations provides a quick tool for obtaining lattice parameters
for ideal crystal structures.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definition streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11. Method reworked
   to better treat triclinic systems.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  With this method there is no guarantee that the resulting parameters
   are for a stable structure. Allowing internal relaxations may result
   in different values for some structures. Additionally, some
   transformation paths may be restricted from occurring due to
   symmetry, i.e. initially cubic structures may remain cubic instead of
   relaxing to a non-cubic structure.

Method and Theory
-----------------

The math in this section uses Voigt notation, where indicies i,j
correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are
orthogonal box vectors.

An initial system (and corresponding unit cell system) is supplied with
box dimensions, :math:`a_i^0`, close to the equilibrium values. A LAMMPS
simulation is performed that evaluates the system’s pressures,
:math:`P_{i}`, for the initial system as given, and subjected to twelve
different strain states corresponding to one of :math:`\epsilon_{i}`
being given a value of :math:`\frac{\Delta \epsilon}{2}`, where
:math:`\Delta \epsilon` is the strain range parameter. Using the
:math:`P_{i}` values obtained from the strained states, the
:math:`C_{ij}` matrix for the system is estimated as

.. math::  C_{ij} \approx - \frac{P_i(\epsilon_j=\frac{\Delta \epsilon}{2}) - P_i(\epsilon_j=-\frac{\Delta \epsilon}{2})}{\Delta \epsilon}.

The negative out front comes from the fact that the system-wide stress
state is :math:`\sigma_i = -P_i`. Using :math:`C_{ij}`, an attempt is
made to compute the elastic compliance matrix as
:math:`S_{ij} = C_{ij}^{-1}`. If successful, new box dimensions are
estimated using :math:`S_{ij}`, :math:`a_i^0`, and :math:`P_i` for the
unstrained system

.. math::  a_i = \frac{a_i^0}{1 - (\sum_{j=1}^3{S_{ij} P_j})}.

The system is updated using the new box dimensions. The process is
repeated until either :math:`a_i` converge less than a specified
tolerance, :math:`a_i` diverge from :math:`a_i^0` greater than some
limit, or convergence is not reached after 100 iterations. If the
calculation is successful, the final :math:`a_i` dimensions are
reported.
