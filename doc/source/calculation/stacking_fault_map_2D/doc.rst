stacking_fault_map_2D calculation style
=======================================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The stacking_fault_map_2D calculation style evaluates the full 2D
generalized stacking fault map for an array of shifts along a specified
crystallographic plane. A regular grid of points is established and the
generalized stacking fault energy is evaluated at each.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Calculation updated to use atomman.defect.StackingFault
   class. Setup and parameter definition streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  The system’s dimension perpendicular to the fault plane should be
   large to minimize the interaction of the free surface and the
   stacking fault.

Method and Theory
-----------------

First, an initial system is generated. This is accomplished using
atomman.defect.StackingFault, which

1. Starts with a unit cell system.

2. Generates a transformed system by rotating the unit cell such that
   the new system’s box vectors correspond to crystallographic
   directions, and filled in with atoms to remain a perfect bulk cell
   when the three boundaries are periodic.

3. All atoms are shifted by a fractional amount of the box vectors if
   needed.

4. A supercell system is constructed by combining multiple replicas of
   the transformed system.

5. The system is then cut by making one of the box boundaries
   non-periodic. A limitation placed on the calculation is that the
   normal to the cut plane must correspond to one of the three Cartesian
   (:math:`x`, :math:`y`, or :math:`z`) axes. If true, then of the
   system’s three box vectors (:math:`\vec{a}`, :math:`\vec{b}`, and
   :math:`\vec{c}`), two will be parallel to the plane, and the third
   will not. The non-parallel box vector is called the cutboxvector, and
   for LAMMPS compatible systems, the following conditions can be used
   to check the system’s compatibility:

   -  cutboxvector = ‘c’: all systems allowed.

   -  cutboxvector = ‘b’: the system’s yz tilt must be zero.

   -  cutboxvector = ‘a’: the system’s xy and xz tilts must be zero.

A LAMMPS simulation performs an energy/force minimization on the system
where the atoms are confined to only relax along the Cartesian direction
normal to the cut plane.

A mathematical fault plane parallel to the cut plane is defined in the
middle of the system. A generalized stacking fault system can then be
created by shifting all atoms on one side of the fault plane by a
vector, :math:`\vec{s}`. The shifted system is then relaxed using the
same confined energy/force minimization used on the non-shifted system.
The generalized stacking fault energy, :math:`\gamma`, can then be
computed by comparing the total energy of the system, :math:`E_{total}`,
before and after :math:`\vec{s}` is applied

.. math::  \gamma(\vec{s}) = \frac{E_{total}(\vec{s}) - E_{total}(\vec{0})}{A},

where :math:`A` is the area of the fault plane, which can be computed
using the two box vectors, :math:`\vec{a_1}` and :math:`\vec{a_2}`, that
are not the cutboxvector.

.. math:: A = \left| \vec{a_1} \times \vec{a_2} \right|,

Additionally, the relaxation normal to the glide plane is characterized
using the center of mass of the atoms above and below the cut plane.
Notably, the component of the center of mass normal to the glide/cut
plane is calculated for the two halves of the the system, and the
difference is computed

.. math::  \delta = \left<x\right>^{+} - \left<x\right>^{-}.

The relaxation normal is then taken as the change in the center of mass
difference after the shift is applied.

.. math::  \Delta\delta = \delta(\vec{s}) - \delta(\vec{0}).

The stacking_fault_map_2D calculation evaluates both :math:`\gamma` and
:math:`\Delta\delta` for a complete 2D grid of :math:`\vec{s}` values.
The grid is built by taking fractional steps along two vectors parallel
to the shift plane.
