## Method and Theory

This calculation is designed to set up, run, and analyze a LAMMPS NEB calculation in which a single atom or a small number of atoms migrates from one low energy configuration to another. The primary use of such a calculation is to evaluate the path and energy barrier associated with a single migration jump of a point defect.

This calculation relies on the NEB method implemented in LAMMPS, as described here https://docs.lammps.org/neb.html.  In short, multiple replicas of the system are constructed to explore the transformation path from one low energy configuration to another low energy configuration.  The atoms in the system are divided into "non-NEB" atoms and "NEB" atoms; the non-NEB atoms will relax normally based on interatomic forces, while the NEB atoms have an additional spring-like force applied to them that keeps their positions intermediate between neighboring replicas.  This allows for the replicas to explore the transformation path between the two end states.

The NEB calculation involves two stages: a relaxation stage in which the replicas are allowed to simultaneously relax towards a minimum energy path, and a climbing stage in which the algorithm searches for the maximum energy along the path, i.e. the energy barrier.

### Defining the atomic configurations

Setting up the calculation requires defining the initial and final configurations and specifying which atoms in the system are NEB atoms and non-NEB atoms.  This is handled by the following parameters of the underlying point_defect_mobility() function

- __system__ is a full atomman.System that defines the non-NEB "background" atoms.
- __point_kwargs__ are atomman.defect.point() operations that can optionally be performed on system to modify the non-NEB atoms.  This is included largely as a convenience so that system can be a bulk crystal configuration for most simple point defect mobility investigations.
- __initialpos__ are the atomic positions of the NEB atoms in the initial reference state.  Atoms at these positions are added to the system to define the full initial configuration.
- __finalpos__ are the atomic positions of the NEB atoms in the final reference state.  Atoms at these positions are added to the system to define the full final configuration.
- __point_symbol__ lists the atom model symbols to associate with the NEB atoms.  Not needed if all atoms are the same species.

#### Example #1: Simple interstitial

With a simple interstitial, system can be a bulk crystal and then the initialpos and finalpos specify where the defect starts and ends.

#### Example #2: Vacancy

Vacancy mobility is actually the mobility of an atom into a nearby vacancy.  The non-NEB system should be a divacancy configuration in which the two vacancy positions correspond to the initialpos and finalpos locations.  This can easily be done with point_kwargs by providing a bulk crystal for system and then adding two vacancies with point_kwargs that have the same positions as initialpos and finalpos. 

#### Example #3: Frenkel-pair formation

The creation of a vacancy and a self-interstitial from a perfect crystal serves as a combination of the two previous examples.  The non-NEB configuration should have a single vacancy, then the initialpos and finalpos should correspond to the vacancy position and the interstitial position, respectively.

#### Example #4: Crowdion/dumbbell interstitials

Crowdion and other dumbbell interstitials are slightly more complicated in that they involve not just the addition of an atom interstitial but the substantial relaxation of at least one other atom in the system.  Other atoms may either need to be initially shifted to avoid overlapping, or multiple atoms can be listed in initialpos and finalpos to be managed by the NEB.  If multiple atoms are NEB controlled, don't forget to remove any duplicates from the non-NEB system.

#### Example #5: Complex environment

Point defect mobilities can also be investigated within more complex, non-bulk configurations.  Such investigations can be performed by providing a system with the more complex environment and using point_kwargs to delete any NEB atoms from the non-NEB list.

### Notes on obtaining good NEB results

- nreplicas sets the number of replica configurations to use.  The larger the number the more computationally expensive the calculation will be but the better the resolution of the path.  If you know the barrier to be symmetric, then using an odd number of replicas will position the middle replica near the barrier.

- springconst is the spring constant for the NEB force applied between replicas.  Weaker spring constants will allow the replicas to preferentially relax towards the low energy configurations and make the sampling of the high energy configurations more sparse.  Stronger spring constants increase the "tension" between replicas and may cause the NEB path to deviate from the true minimum energy path.  Selecting the optimum springconst value may require trial and error as the value is influenced by the path being explored, materials constants, and the number of replicas.

- Ideally, each NEB calculation should move from one low energy (meta)stable configuration to another through a single energy barrier.  If you run a calculation and see multiple barriers then it is recommended to run separate NEBs for each barrier jump by changing the end configurations to each intermediate minima.

- If the NEB calculation fails to converge within the minsteps/climbsteps, first check the replica configurations. 
    - Have the end configurations relaxed and transformed into a different type of configuration?
    - Are the NEB atom trajectories for the unrelaxed configurations doing something inappropriate, like passing through the position of another atom?
    - Are there multiple energy barriers indicating a complex multi-step path?

- If the path seems appropriate but convergence is still not reached, try different numbers of replicas and spring constant values.  
    - If you are only interested in the energy barrier value, then it is likely enough to find one (nreplicas, springconst) combination that converges.
    - If the specific path is important as well then you should explore the sensitivity of the path to the springconst.
