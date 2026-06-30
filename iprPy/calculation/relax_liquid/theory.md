## Method and Theory

### Simulation runs

This calculation performs up to three MD simulation stages based on the inputs to generate an equilibrium liquid phase

1. Melt stage: MD is performed at an elevated temperature to ensure that a liquid phase is formed.
2. Equilibrium stage: MD is performed at the lower target temperature but no analysis output is generated.
3. Analysis stage: MD continues at the target temperature and thermo data and dump configuration files are generated.

All three stages use the NPT Nose-Hoover style thermostat+barostat with all three box dimensions coupled together. This allows for the system to relax to a target pressure while preventing any of the box dimensions from shrinking too small for the RDF calculations.

Additionally, the calculation supports optionally creating new velocities for all atoms prior to performing MD.  This is useful if starting from an ideal atomic configuration, or for running repeat simulation tests to evaluate the methodology error.

The first two MD stages are optional and can be skipped by specifying 0 steps be performed for either/both stages. Skipping the melt stage is useful if you are starting from a known liquid configuration. Skipping the equilibrium stage is not recommended unless you are starting from a known liquid configuration already equilibrated at the target temperature.

### RDF calculation

The radial distribution function (RDF) for the liquid is computed from the dump files generated during the analysis stage. For each dump file, atomic neighbor lists are constructed for all atoms within a given cutoff distance, and the neighbor list counts are binned based on radial distances. The RDF is then computed by dividing by the expected density of each bin's radial shell based on the ideal bulk density.  To generate smooth curves, the RDF values are averaged across all dump files.

*Note* The RDF calculations are performed using the atomman.thermo.RDF class rather than using the LAMMPS compute rdf option.  This is done as by default the LAMMPS version only allows RDFs out to the potential's cutoff to be computed.  With the atomman class, RDFs can be computed out to larger cutoffs. With the atomman method, the maximum allowed RDF cutoff is 1/2 the smallest periodic distance of the system as atomman's neighbor list method does not differentiate between replicas of the same atom. Also note that the RDF calculation will quickly increase in computational cost as the cutoff increases due to the increasing number of neighbor atoms to account for.  