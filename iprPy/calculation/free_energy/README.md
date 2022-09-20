# relax_box calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The free_energy calculation style uses thermodynamic integration to evaluate
the absolute Helmholtz and Gibbs free energies of a solid phase by comparing
it to a reference Einstein solid. 

### Version notes

- 2022-09-20: Calculation first added to iprPy

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The simulations used by this method are all fixed volume and therefore will not relax the system to a given pressure. Instead, it is expected that the given system is already relaxed to the target pressure of interest.
