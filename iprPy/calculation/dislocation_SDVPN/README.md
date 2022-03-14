# dislocation_SDVPN calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The dislocation_SDVPN calculation style predicts a dislocation's planar spreading using the semidiscrete variational Peierls-Nabarro method.  The solution finds the disregistry (difference in displacement above and below the slip plane) that minimizes the dislocation's energy.  The energy term consists of two primary components: an elastic component due to the dislocation interacting with itself, and a misfit component arising from the formation of a generalized stacking fault along the dislocation's spreading.

### Version notes

- 2018-09-25: Notebook added
- 2019-07-30: Notebook setup and parameters changed.
- 2020-09-22: Notebook updated to reflect changes in the calculation method due to updates in atomman's Volterra class solution generators.  Setup and parameter definitions streamlined.
- 2022-03-11: Notebook updated to reflect version 0.11.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The calculation method solves the problem using a 2D generalized stacking fault energy map.  Better results may be possible by measuring a full 3D map, but that would require adding a new calculation for the 3D variation.
- The implemented method is suited for dislocations with planar spreading. It is not suited for dislocations that spread on multiple atomic planes, like the a/2<111> bcc screw dislocation.
- While the solution is taken at discrete points that (typically) correspond to atomic sites, the underlying method is still a continuum solution that does not fully account for the atomic nature of the dislocation.
