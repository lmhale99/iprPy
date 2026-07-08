## Simulation design

The viscosity_driving calculation evaluates the viscosity of a liquid using the cosine periodic perturbation method. This uses the LAMMPS commands fix accelerate/cos and compute viscosity/cos to apply a periodic external acceleration to the atoms in the simulation, then estimate the viscosity based on the resulting velocity profile.  The simulation is sensitive to the amplitude of the acceleration used.

See the associated LAMMPS commands for more details: https://docs.lammps.org/fix_accelerate_cos.html and https://docs.lammps.org/compute_viscosity_cos.html.

