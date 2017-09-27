
Introduction
************

The **stacking_fault** calculation evaluates the energy of a single
generalized stacking fault shift along a specified crystallographic
plane.

**Disclaimer #1**: The system's dimension perpendicular to the fault
plane should be large to minimize the interaction of the free surface
and the stacking fault.

**Disclaimer #2**: Currently, the rotation capabilities of atomman
limit this calculation such that only cubic prototypes can be rotated.
Properties of non-cubic structures can still be explored, as long as
the configuration being loaded has the plane of interest perpendicular
to one of the three box vectors.
