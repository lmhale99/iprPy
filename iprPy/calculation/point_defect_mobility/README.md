# point_defect_mobility calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Jacob Hechter** 

## Introduction

The point_defect_mobility calculation style uses a nudged elastic band (NEB) calculation to evaluate the energy barrier and path associated with point defects moving from one low energy configuration to another.

### Version notes

- 2019-8-09: Calculation created by Jacob Hechter.
- 2024-4-24: Calculation updated to current iprPy, and code and methodology cleaned up.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- NEB works best when exploring a single barrier path between two (meta)stable configurations.  If the end states are not local energy minima then they may transform into a different configuration so you should always check the initial and final configurations after relaxation.  If you see multiple energy peaks then the path involves more than one step that should be divided into separate NEB calculations to independently capture each barrier.
- The NEB calculation evaluates the energies as a function of reaction coordinates along the computed path.  The reaction coordinates come from the NEB algorithm and may not directly correspond to any actual physical coordinates.  For physical coordinates, it is better to use the measured position(s) of the NEB atom(s) instead.
- Intermediate replicas are held in place by applying a force on the NEB atoms based on a spring-like function.  NEB calculations can be sensitive to the associated spring constant, with optimum values often dependent on the specific calculation.  The weaker the spring constant, the more the replicas will preferentially relax towards the low energy end configurations.  The stronger the spring constant, the larger the "tension" will be between replicas that can cause the NEB path to deviate from the true minimum energy path.  


