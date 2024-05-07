# elastic_constants_dynamic calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The elastic_constants_dynamic calculation style computes the elastic constants, $C_{ij}$, for a system using the fluctuation method through computing the Born matrix.  This should provide elastic constants estimates comparable to elastic_constants_static for 0K calculations and relatively quick evaluations of elastic constants at higher temperatures.

### Version notes

- 2024-04-25 Calculation method based on the fluctuations/born matrix method finalized.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- This calculation does not perform any relaxations on the box dimensions.  As the elastic constants are sensitive to both temperature and pressure, be sure to properly relax your system before passing it into this calculation.
- Estimates of the second derivative of energy with respect to strain are computed numerically using a small strain value.  The computed elastic constants may be sensitive to the choice in strain.  The best values are obtained by strains that are large enough to overcome numerical issues with precision while small enough so that the elastic behavior is still in the linear regime.
