
Introduction
************

The **dislocation_monopole** calculation calculation inserts a
dislocation monopole into an atomic system using the anisotropic
elasticity solution for a straight perfect dislocation, and relaxes
the atomic configuration. The atoms within the active region of the
system are then relaxed statically or dynamically. The relaxed
dislocation system and corresponding dislocation-free base systems are
retained in the calculation's archived record. Various properties
associated with the dislocation's elasticity solution are recorded in
the calculation's results record.

**Disclaimer #1**: In principle, the theory should allow for a
straight dislocation monopole to be added to any crystal structure. In
practice, the methodology is currently only fully compatible for cubic
systems. First, atomman is currently limited to applying rotations to
cubic systems. Second, the methodology currently limits the
dislocation to being inserted along the z-axis. See Method and Theory
for more details.

**Disclaimer #2**: Only performing a static relaxation is considerably
faster than performing a dynamic relaxation, but it may not fully
relax the configuration.

**Disclaimer #3**: The sizes of the system and boundary region should
be selected to place the dislocation far from the boundary region to
reduce the effect of the boundary region on the dislocation.
