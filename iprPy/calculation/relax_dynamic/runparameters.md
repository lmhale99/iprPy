### Run parameters

Provides parameters specific to the calculation at hand.

- __temperature__: temperature in Kelvin at which to run the MD integration scheme at.  Default value is '0'.
- __pressure_xx, pressure_yy, pressure_zz, pressure_xy, pressure_xz, pressure_yz__: specifies the pressures to relax the box to.  Default values are '0 GPa' for all.
- __integrator__: specifies which MD integration scheme to use.  Default value is 'nph+l' for temperature = 0, and 'npt' otherwise.
- __thermosteps__: specifies how often LAMMPS prints the system-wide thermo data.  Default value is runsteps/1000, or 1 if runsteps is less than 1000.
- __dumpsteps__: specifies how often LAMMPS saves the atomic configuration to a LAMMPS dump file.  Default value is runsteps, meaning only the first and last states are saved.
- __runsteps__: specifies how many timesteps to integrate the system.  Default value is 100000.
- __equilsteps__: specifies how many timesteps are ignored as equilibration time when computing the mean box parameters.  Default value is 10000.
- __randomseed__: provides a random number seed to generating the initial atomic velocities.  Default value gives a random number as the seed.
