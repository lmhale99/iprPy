# dislocation_SDVPN Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-09-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The __dislocation_SDVPN__ calculation predicts a dislocation's planar spreading using the semidiscrete variational Peierls-Nabarro method.  The solution finds the disregistry (difference in displacement above and below the slip plane) that minimizes the dislocation's energy.  The energy term consists of two primary components: an elastic component due to the dislocation interacting with itself, and a misfit component arising from the formation of a generalized stacking fault along the dislocation's spreading.

__Disclaimer #1__: The calculation method solves the problem using a 2D generalized stacking fault energy map.  Better results may be possible by measuring a full 3D map, but that would require adding a new calculation for the 3D variation.

__Disclaimer #2__: The implemented method is suited for dislocations with planar spreading. It is not suited for dislocations that spread on multiple atomic planes, like the a/2<111> bcc screw dislocation.

__Disclaimer #3__: While the solution is taken at discrete points that (typically) correspond to atomic sites, the underlying method is still a continuum solution that does not fully account for the atomic nature of the dislocation.