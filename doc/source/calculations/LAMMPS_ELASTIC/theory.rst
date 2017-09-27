Method and Theory
-----------------

The math in this section uses Voigt notation, where indicies i,j
correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are
orthogonal box vectors.

An initial system (and corresponding unit cell system) is supplied with
box dimensions, :math:`a_i^0`, close to the equilibrium values. A LAMMPS
simulation performs an energy/force minimization with a fix box\_relax
option to relax both the local atomic coordinates and the system's
dimensions. The pressures, :math:`P_{i}`, of the relaxed state are
recorded.

Further energy/force minimizations are then performed without box\_relax
to evaluate :math:`P_{i}` at twelve different strain states
corresponding to one of :math:`\epsilon_{i}` being given a value of
:math:`\pm \Delta \epsilon`, where :math:`\Delta \epsilon` is the strain
range parameter. Using the :math:`P_{i}` values obtained from the
strained states, the :math:`C_{ij}` matrix for the system is estimated
as

.. math::  C_{ij} \approx \frac{C_{ij}^+ + C_{ij}^-}{2}, 

where

.. math::  C_{ij}^+ = - \frac{P_i(\epsilon_j=\Delta \epsilon) - P_i(\epsilon_j=0)}{\Delta \epsilon}.

.. math::  C_{ij}^- = - \frac{P_i(\epsilon_j=0) - P_i(\epsilon_j=-\Delta \epsilon)}{\Delta \epsilon}.

The negative out front comes from the fact that the system-wide stress
state is :math:`\sigma_i = -P_i`.

The full process is repeated until the box dimensions from one iteration
to the next are within the specified relative convergence tolerance.
