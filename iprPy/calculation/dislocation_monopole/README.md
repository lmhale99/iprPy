# dislocation_monopole Calculation

- - -

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2017-07-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 

- - -

## Introduction

The __dislocation_monopole__ calculation calculation inserts a dislocation monopole into an atomic system using the anisotropic elasticity solution for a straight perfect dislocation, and relaxes the atomic configuration. The atoms within the active region of the system are then relaxed statically or dynamically. The relaxed dislocation system and corresponding dislocation-free base systems are retained in the calculation's archived record. Various properties associated with the dislocation's elasticity solution are recorded in the calculation's results record.

__Disclaimer #1__: In principle, the theory should allow for a straight dislocation monopole to be added to any crystal structure. In practice, the methodology is currently only fully compatible for cubic systems. First, atomman is currently limited to applying rotations to cubic systems. Second, the methodology currently limits the dislocation to being inserted along the z-axis. See Method and Theory for more details.

__Disclaimer #2__: Only performing a static relaxation is considerably faster than performing a dynamic relaxation, but it may not fully relax the configuration.

__Disclaimer #3__: The sizes of the system and boundary region should be selected to place the dislocation far from the boundary region to reduce the effect of the boundary region on the dislocation. 