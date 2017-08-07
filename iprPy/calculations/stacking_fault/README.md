# stacking_fault Calculation

- - -

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2017-07-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
- - -

## Introduction

This Notebook describes the methodology for both the __stacking_fault__ and __stacking_fault_multi__ calculations.

The __stacking_fault__ calculation evaluates the energy of a single generalized stacking fault shift along a specified crystallographic plane. In other words, this evaluates only a single configuration. This calculation script is better for evaluating critical points with known shifts, or for implementation in an intelligent workflow.   

The __stacking_fault_multi__ calculation evaluates the full 2D generalized stacking fault map for an array of shifts along a specified crystallographic plane. A regular grid of points is established and the generalized stacking fault energy is evaluated at each. This calculation script is better optimized for generating the full GSF maps as it reduces simulation setup time and all values are saved to a single record.

__Disclaimer #1__: The system's dimension perpendicular to the fault plane should be large to minimize the interaction of the free surface and the stacking fault.

__Disclaimer #2__: Currently, the rotation capabilities of atomman limit this calculation such that only cubic prototypes can be rotated. Properties of non-cubic structures can still be explored, as long as the configuration being loaded has the plane of interest perpendicular to one of the three box vectors.