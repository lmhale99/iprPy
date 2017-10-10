# point_defect_diffusion Calculation

- - -

**Lucas M. Hale**, [lucas.hale@nist.gov](mailto:lucas.hale@nist.gov?Subject=ipr-demo), *Materials Science and Engineering Division, NIST*.

**Chandler A. Becker**, [chandler.becker@nist.gov](mailto:chandler.becker@nist.gov?Subject=ipr-demo), *Office of Data and Informatics, NIST*.

**Zachary T. Trautt**, [zachary.trautt@nist.gov](mailto:zachary.trautt@nist.gov?Subject=ipr-demo), *Materials Measurement Science Division, NIST*.

Version: 2017-09-27

[Disclaimers](http://www.nist.gov/public_affairs/disclaimer.cfm) 
 
- - -

## Introduction

The point_defect_diffusion calculation estimates the diffusion rate of a point defect at a specified temperature.  A system is created with a single point defect, and subjected to a long time molecular dynamics simulation.  The mean square displacement for the defect is computed, and used to estimate the diffusion constant.

__Note__: the current version estimates the defect's diffusion by computing the mean square displacement of all atoms in the system.  This is useful for estimating rates associated with vacancies and self-interstitials as the process is not confined to a single atom's motion.  However, this makes the calculation ill-suited to measuring diffusion of impurities in its current form. 