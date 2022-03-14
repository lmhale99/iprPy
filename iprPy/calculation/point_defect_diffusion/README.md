# point_defect_diffusion calculation style

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

Description updated: 2019-07-26

## Introduction

The point_defect_diffusion calculation style estimates the diffusion rate of a point defect at a specified temperature.  A system is created with a single point defect, and subjected to a long time molecular dynamics simulation.  The mean square displacement for the defect is computed, and used to estimate the diffusion constant.

### Version notes

- 2022-03-11: Notebook updated to reflect version 0.11.

### Additional dependencies

### Disclaimers

- [NIST disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm)
- The calculation estimates the defect's diffusion by computing the mean square displacement of all atoms in the system.  This is useful for estimating rates associated with vacancies and self-interstitials as the process is not confined to a single atom's motion.  However, this makes the calculation ill-suited to measuring diffusion of substitutional impurities as it does not individually track each atom's position throughout.
