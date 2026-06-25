# relax_dynamic calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

## Introduction

The relax_dynamic calculation style dynamically relaxes an atomic configuration for a specified number of timesteps.  Upon completion, the mean, $\langle X \rangle$, and standard error, $\sigma_{\langle X \rangle}$, of all thermo properties, $X$, are computed for a specified range of times.  This method is meant to measure equilibrium properties of bulk materials, both at zero K and at various temperatures.

### Version notes

- 2018-07-09: Notebook added.
- 2019-07-30: Description updated and small changes due to iprPy version.
- v0.10.0: Version 0.10 update - potentials now loaded from database.
- 2020-09-22: Setup and parameter definition streamlined.
- v0.11.0: Notebook updated to reflect version 0.11.  Restart capability added in.
- v0.12.0: Method updated to support the LAMMPS library interface.  Updates were also made to make the calculation more consistent with others in iprPy, such as it now returns the standard error rather than the standard deviation of the measured values.
  
### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The calculation reports the standard error of the mean, $\sigma_{\langle X \rangle}$, which is computed from the standard deviation, $\sigma_X$.  The two are related according to $\sigma_{\langle X \rangle} = \sigma_X \sqrt{\frac{1}{N}}$, where $N$ is the number of uncorrelated samples taken of $X$. For this calculation we take all thermo outputs as samples and assume they are uncorrelated, which is probably a decent assumption for thermostep $\ge$ 100.