# relax_liquid calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The relax_liquid calculation style is designed to generate and characterize a liquid phase configuration for an atomic potential based on an initial configuration, target temperature and target pressure.  The calculation involves multiple stages of relaxation and computes the mean squared displacement and radial distribution functions on the final liquid.

### Version notes

- 2022-10-12: Calculation created

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- No active checks are performed by this calculation to ensure that the system is liquid. Be sure to check the final atomic configurations. The thermo output can also provide a rough guideline in that you should see convergence of volume but not of the individual lx, ly, lz dimensions for a liquid phase.
- If starting with a crystalline configuration, be sure to use an adequately high melt temperature and number of melt steps.
- The temperature and volume equilibrium stages are designed to get the final nve system close to the target temperature and pressure, but they will not be exact.  Be sure to check that the measured temperature and pressure are close to the targets.
