
Introduction
************

The point_defect_diffusion calculation estimates the diffusion rate of
a point defect at a specified temperature. A system is created with a
single point defect, and subjected to a long time molecular dynamics
simulation. The mean square displacement for the defect is computed,
and used to estimate the diffusion constant.

**Note**: the current version estimates the defect's diffusion by
computing the mean square displacement of all atoms in the system.
This is useful for estimating rates associated with vacancies and
self-interstitials as the process is not confined to a single atom's
motion. However, this makes the calculation ill-suited to measuring
diffusion of impurities in its current form.
