elastic_constants_static calculation style
==========================================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The elastic_constants_static calculation style computes the elastic
constants, :math:`C_{ij}`, for a system by applying small strains and
performing static energy minimizations of the initial and strained
configurations. Three estimates of the elastic constants are returned:
one for applying positive strains, one for applying negative strains,
and a normalized estimate that averages the ± strains and the symmetric
components of the :math:`C_{ij}` tensor.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Setup and parameter definition streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  Unlike the previous LAMMPS_ELASTIC calculation, this calculation does
   *not* perform a box relaxation on the system prior to evaluating the
   elastic constants. This allows for the static elastic constants to be
   evaluated for systems that are relaxed to different pressures.
-  The elastic constants are estimated using small strains. Depending on
   the potential, the values for the elastic constants may vary with the
   size of the strain. This can come about either if the strain exceeds
   the linear elastic regime.
-  Some classical interatomic potentials have discontinuities in the
   fourth derivative of the energy function with respect to position. If
   the strained states straddle one of these discontinuities the
   resulting static elastic constants values will be nonsense.

Method and Theory
-----------------

The calculation method used here for computing elastic constants is
based on the method used in the ELASTIC demonstration script created by
Steve Plimpton and distributed with LAMMPS.

The math in this section uses Voigt notation, where indicies i,j
correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are
orthogonal box vectors.

A LAMMPS simulation performs thirteen energy/force minimizations

-  One for relaxing the initial system.

-  Twelve for relaxing systems in which a small strain of magnitude
   :math:`\Delta \epsilon` is applied to the system in both the positive
   and negative directions of the six Voigt strain components,
   :math:`\pm \Delta \epsilon_{i}`.

The system virial pressures, :math:`P_{i}`, are recorded for each of the
thirteen relaxed configurations. Two estimates for the :math:`C_{ij}`
matrix for the system are obtained as

.. math::  C_{ij}^+ = - \frac{P_i(\Delta \epsilon_j) - P_i(0)}{\Delta \epsilon},

.. math::  C_{ij}^- = - \frac{P_i(0) - P_i(-\Delta \epsilon_j)}{\Delta \epsilon}.

The negative out front comes from the fact that the system-wide stress
state is :math:`\sigma_i = -P_i`. A normalized, average estimate is also
obtained by averaging the positive and negative strain estimates, as
well as the symmetric components of the tensor

.. math::  C_{ij} = \frac{C_{ij}^+ + C_{ij}^- + C_{ji}^+ + C_{ji}^-}{4}.
