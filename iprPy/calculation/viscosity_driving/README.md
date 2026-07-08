# viscosity_driving calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The viscosity_driving calculation style estimates the viscosity of a liquid by applying a sinusoidal acceleration to the system.

### Version notes

- 2025-??: Initial version of the calculation added.
- 2026-: Calculation updated for the new LAMMPS interface.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The computed viscosity can be sensitive to the acceleration parameter. Accelerations that are too large can fracture the liquid, while accelerations too small will result in large noise in the measurement. The best values relate to the material's viscosity, so trying different accelerations may be useful/necessary.