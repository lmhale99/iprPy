Method and Theory
-----------------

System orientation considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Properly constructing a periodic array of dislocations atomic
configuration requires careful consideration of dislocation solutions
and atomic system boundaries. Solutions for straight dislocations based
on elasticity often follow the convention of using a Cartesian system
(:math:`x', y', z'`) in which the dislocation line is oriented along the
:math:`z'`-axis, and the slip plane taken to be the :math:`y'=0` plane.
The dislocation’s Burgers vector, :math:`\vec{b}`, is then in the
:math:`x'z'`-plane, with edge component in the :math:`x'`-direction and
screw component in the :math:`z'`-direction. When the dislocation slips,
the dislocation line will move in the :math:`x'`-direction.

For any such dislocation solution, there will be a shearing along the
slip plane resulting in disregistry, i.e. a relative displacement
between the top and bottom halves. This disregistry has limits such that
it is :math:`0` for :math:`x' \to -\infty` and :math:`\vec{b}` for
:math:`x' \to +\infty`.

Within an atomic system, the dislocation line should be aligned with one
of the system’s box vectors making the dislocation infinitely long and
initially perfectly straight. The slip plane can then be defined as
containing that box vector and another one. This results in the third
box vector being the only one with a component parallel to the slip
plane’s normal.

For LAMMPS-based simulations, the most convenient orientation to use is
to align the dislocation with the :math:`\vec{a}` box vector, and to
define the slip plane as containing both :math:`\vec{a}` and
:math:`\vec{b}`. Given the limits that LAMMPS places on how system boxes
can be defined, this results in favorable alignment of the system to the
LAMMPS Cartesian system (:math:`x, y, z`). The dislocation line will be
along the :math:`x`-axis, the slip plane normal parallel to the
:math:`z`-axis, and dislocation motion will be in the :math:`y`
direction. Thus, the LAMMPS coordinates corresponds to a rotation of the
theory coordinates such that :math:`x'=y, y'=z, z'=x`.

Linear displacements solution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to insert a dislocation is to cut the system in half
along the slip plane and apply equal but opposite linear displacements,
:math:`\vec{u}`, to the two halves with end conditions

-  :math:`\vec{u}(y=-\frac{Ly}{2}) = 0`
-  :math:`\vec{u}(y=\frac{Ly}{2}) = \pm \frac{\vec{b}}{2}`

Applying these displacements results in a disregistry along the slip
plane that ranges from :math:`0` to :math:`\vec{b}`. While the two
:math:`y` boundaries of the system both correspond to a perfect crystal,
they are misaligned from each other by :math:`\frac{\vec{b}}{2}`. A
coherent periodic boundary along the :math:`\vec{b}` box vector can be
established by adding or subtracting :math:`\frac{\vec{b}}{2}` from
:math:`\vec{b}`.

Note that with dislocations containing an edge component, a half-plane
of atoms either needs to be inserted or removed to ensure boundary
compatibility. Here, this is accomplished by always shifting
:math:`\vec{b}` to be shorter in the :math:`y` direction, and removing
excess atoms by identifying (near) duplicates.

Using dislocation solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A slightly more complicated, but ultimately more efficient, way of
creating a periodic array of dislocations system is to combine the
linear displacements solultion above with a more accurate linear elastic
dislocation solution. The linear solution is used for the atoms at the
free surfaces in the :math:`z` direction, and for ensuring periodicity
across the :math:`\vec{b}` box vector direction. The linear elastic
dislocation solution is then used for atoms in the middle of the system
to construct an initial dislocation.
