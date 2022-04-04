surface_energy_static calculation style
=======================================

**Lucas M. Hale**,
`lucas.hale@nist.gov <mailto:lucas.hale@nist.gov?Subject=ipr-demo>`__,
*Materials Science and Engineering Division, NIST*.

Introduction
------------

The surface_energy_static calculation style evaluates the formation
energy for a free surface by slicing an atomic system along a specific
plane.

Version notes
~~~~~~~~~~~~~

-  2018-07-09: Notebook added.
-  2019-07-30: Description updated and small changes due to iprPy
   version.
-  2020-05-22: Version 0.10 update - potentials now loaded from
   database.
-  2020-09-22: Calculation updated to use atomman.defect.FreeSurface
   class. Setup and parameter definition streamlined.
-  2022-03-11: Notebook updated to reflect version 0.11.

Additional dependencies
~~~~~~~~~~~~~~~~~~~~~~~

Disclaimers
~~~~~~~~~~~

-  `NIST
   disclaimers <http://www.nist.gov/public_affairs/disclaimer.cfm>`__
-  Other atomic configurations at the free surface for certain planar
   cuts may have lower energies. The atomic relaxation will find a local
   minimum, which may not be the global minimum. Additionally, the
   material cut is planar perfect and therefore does not explore the
   effects of atomic roughness.

Method and Theory
-----------------

First, an initial system is generated. This is accomplished by

1. Starting with a unit cell system.

2. Generating a transformed system by rotating the unit cell such that
   the new system’s box vectors correspond to crystallographic
   directions, and filled in with atoms to remain a perfect bulk cell
   when the three boundaries are periodic.

3. All atoms are shifted by a fractional amount of the box vectors if
   needed.

4. A supercell system is constructed by combining multiple replicas of
   the transformed system.

Two LAMMPS simulations are then performed that apply an energy/force
minimization on the system, and the total energy of the system after
relaxing is measured, :math:`E_{total}`. In the first simulation, all of
the box’s directions are kept periodic (ppp), while in the second
simulation two are periodic and one is non-periodic (ppm). This
effectively slices the system along the boundary plane creating two free
surfaces, each with surface area

.. math:: A = \left| \vec{a_1} \times \vec{a_2} \right|,

where :math:`\vec{a_1}` and :math:`\vec{a_2}` are the two lattice
vectors corresponding to the periodic in-plane directions.

The formation energy of the free surface, :math:`E_{f}^{surf}`, is
computed in units of energy over area as

.. math:: E_{f}^{surf} = \frac{E_{total}^{surf} - E_{total}^{0}} {2 A}.

The calculation method allows for the specification of which of the
three box dimensions the cut is made along. If not specified, the
default behavior is to make the :math:`\vec{c}` vector direction
non-periodic. This choice is due to the limitations of how LAMMPS
defines triclinic boxes. :math:`\vec{c}` vector is the only box vector
that is allowed to have a component in the Cartesian z direction.
Because of this, the other two box vectors are normal to the z-axis and
therefore will be in the cut plane.
