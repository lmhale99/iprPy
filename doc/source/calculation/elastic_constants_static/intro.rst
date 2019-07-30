Introduction
============

The elastic_constants_static calculation style computes the elastic
constants, :math:`C_{ij}`, for a system by applying small strains and
performing static energy minimizations of the initial and strained
configurations. Three estimates of the elastic constants are returned:
one for applying positive strains, one for applying negative strains,
and a normalized estimate that averages the ± strains and the symmetric
components of the :math:`C_{ij}` tensor.

Version notes
~~~~~~~~~~~~~

-  This calculation style and relax_static replace the previous
   LAMMPS_ELASTIC calculation style.

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
