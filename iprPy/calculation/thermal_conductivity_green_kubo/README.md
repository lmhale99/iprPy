# thermal_conductivity_green_kubo calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The thermal_conductivity_green_kubo calculation style evaluates the thermal conductivity of a system at equilibrium using the Green-Kubo method.

### Version notes

- v0.12.0: Calculation added.
  
### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- This calculation can only capture the classical non-electronic component of thermal conductivity. It is best suited for non-conductive materials at temperatures above their Debye temperatures.
- Convergence of the autocorrelation function to zero at large time deltas is sensitive to the material, potential and temperature.  Always check the computed autocorrelation function!
