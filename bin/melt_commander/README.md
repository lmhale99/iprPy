# MeltCommander

The MeltCommander class provides an example workflow for iteratively performing the iprPy melting_temperature calculation to obtain multiple meaningful melting temperature estimates.  The workflow can be ran independently for any LAMMPS interatomic potential in the iprPy database, and the calculation results are integrated into the same iprPy database like other calculations.

## MeltCommander workflow outline

1. User specifies 
    - The database to interact with,
    - The LAMMPS command (and mpi command) to use for simulating,
    - The interatomic potential to use,
    - The crystal prototype and composition for the solid phase, and
    - Upper and lower bounds for temperature_guess.
2. A melting_temperature calculation is prepared and ran at some temperature_guess within the bounded region.
3. Upon completion, the estimated solid fraction is extracted from the calculation results.
    - If the solid fraction is > 0.75 or < 0.25, the bounds for temperature_guess are adjusted accordingly.  The temperature_guess for the next iteration is set to be halfway between the new bounded region.
    - If the solid fraction is < 0.75 and > 0.25, the melting temperature estimate is considered good and is retained.  Within this range, if the solid fraction is > 0.6 or < 0.4, then the next temperature_guess is taken as being halfway between the current temperature_guess and the far bound.  The calculation's random seed for the next simulation is increased by 1 to prevent any repeat simulations.
4. Steps 2 and 3 are repeated until the wanted number of good melting temperature estimates are obtained, or the process is cancelled because no good results are being generated.

## Future improvements

The MeltCommander is still in development and as such has lots of room to improve.  This section lists things to be implemented later...

- Support for all 8 crystal structures recognized by the polyhedral template matching algorithm in LAMMPS.
- The system size multipliers and other run settings should be made as accessible parameters and input script terms rather than being hard-coded.
- The search criteria in Step 3 work decently well, but can occasionally fail due to the random nature of the simulations.  Adjustments to the criteria or a complete replacement of them may be warranted.
- There are currently no automatic "failure" stopping criteria for the iteration loop.  Something simple like an upper limit on total iterations or perhaps something smarter like upper and lower bounds are too close together.
- It is likely warranted to fully incorporate this into iprPy later rather than just as a supplemental script distributed with it.