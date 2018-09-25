Method and Theory
-----------------

The math in this section uses Voigt notation, where indicies i,j
correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are
orthogonal box vectors.

An initial system (and corresponding unit cell system) is supplied with
box dimensions, :math:`a_i^0`, close to the equilibrium values. A LAMMPS
simulation is performed that evaluates the system's pressures,
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
