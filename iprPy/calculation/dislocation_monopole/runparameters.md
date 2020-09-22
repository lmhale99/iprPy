### Run Parameters

Provides parameters specific to the calculation at hand.

- __annealtemperature__: specifies the temperature at which to anneal the dislocation system.
- __annealsteps__: specifies how many MD steps to perform at the anneal temperature before running the energy/force minimization.  Default value is 0 if annealtemperature=0, and 10,000 if annealtemperature > 0.
- __randomseed__: provides a random number seed to generating the initial atomic velocities.  Default value gives a random number as the seed.
- __dislocation_boundaryshape__: 'box' or 'cylinder' specifying the resulting shape of the active region after defining the boundary atoms.  For 'box', the boundary width is constant at the two non-periodic box edges.  For 'cylinder', the active region is a cylinder centered around the dislocation line.  Default value is 'cylinder'.
- __dislocation_boundarywidth__: floating point number specifying the minimum thickness of the boundary region.
- __dislocation_boundaryscale__: boolean indicating if the boundary width is taken as absolute (False) or should be scaled by the loaded unit cell's a lattice parameter.
