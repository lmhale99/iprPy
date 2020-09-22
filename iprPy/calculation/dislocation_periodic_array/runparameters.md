### Run Parameters

Provides parameters specific to the calculation at hand.

- __annealtemperature__: specifies the temperature at which to anneal the dislocation system.
- __annealsteps__: specifies how many MD steps to perform at the anneal temperature before running the energy/force minimization.  Default value is 0 if annealtemperature=0, and 10,000 if annealtemperature > 0.
- __randomseed__: provides a random number seed to generating the initial atomic velocities.  Default value gives a random number as the seed.
- __dislocation_duplicatecutoff__: floating point specifying the cutoff distance to use for determining duplicate atoms to delete associated with the extra half-plane formed by a dislocation's edge component.  Default value is 0.5 Angstroms.
- __dislocation_boundarywidth__: floating point number specifying the minimum thickness of the boundary region.
- __dislocation_boundaryscale__: boolean indicating if the boundary width is taken as absolute (False) or should be scaled by the loaded unit cell's a lattice parameter.
- __dislocation_onlylinear__: boolean, which if True will only use linear gradient displacements to form the dislocation and not the Volterra solution displacements.  Setting this to be True is useful for screw dislocations that dissociate as it ensures that the resulting structure will dissociate along the correct slip plane.
