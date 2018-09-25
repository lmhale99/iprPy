# relax_dynamic Calculation

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2018-06-24

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)

## Introduction

The relax_dynamic calculation dynamically relaxes an atomic configuration for a specified number of timesteps.  Upon completion, the mean, $<X>$, and standard deviation, $\sigma_X$, of all thermo properties, $X$, are computed for a specified range of times.  This method is meant to measure equilibrium properties of bulk materials, both at zero K and at various temperatures.

__Version notes__: This was previously called the dynamic_relax calculation and was renamed for consistency with other calculations.

__Disclaimer #1__: The calculation reports the standard deviation, $\sigma_X$ of the measured properties not the standard error of the mean, $\sigma_{<X>}$.  The two are related to each other according to

$$ \sigma_{<X>} = \sigma_X \sqrt{\frac{C}{N}} $$,

where $N$ is the number of samples taken of $X$, and $C$ is a statistical inefficiency due to the autocorrelation of the measurements with time.  Obtaining a proper estimate of $\sigma_{<X>}$ requires either estimating $C$ from the raw thermo data (not done here), or only taking measurements sporadically to ensure the samples are independent.

__Disclaimer #2__: Good (low error) results requires running large simulations for a long time.  The reasons for this are:

- Systems have to be large enough to avoid issues with fluctuations across the periodic boundaries.

- Runs must first let the systems equilibrate before meaningful measurements can be taken.

- The standard deviation, $\sigma$, of thermo properties is proportional to the number of atoms, $N_a$ as $\sigma \propto \frac{1}{\sqrt{N_a}}$.

- The standard error, $\sigma_x$ of thermo properties is proportional to the number of samples taken, $N$ as $\sigma_x \propto \frac{1}{\sqrt{N}}$.