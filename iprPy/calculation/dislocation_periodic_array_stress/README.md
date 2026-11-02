# dislocation_periodic_array_stress Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Version: 2026-09-28

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The dislocation_periodic_array_stress calculation takes a previously generated periodic array of dislocations configuration consistent with the output of the dislocation_periodic_array calculation and subjects it to a constant shear stress. The system is then allowed to evolve during molecular dynamics iterations and assuming the combined temperature and stress are large enough the dislocation in the system should begin to glide at a consistent rate.