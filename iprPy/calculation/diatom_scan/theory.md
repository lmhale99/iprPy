## Method and Theory

Two atoms are placed in an otherwise empty system.  The total energy of the system is evaluated for different interatomic spacings.  This provides a means of evaluating the pair interaction component of an interatomic potential, which is useful for a variety of reasons

- The diatom_scan is a simple calculation that can be used to fingerprint a given interaction.  This can be used to help determine if two different implementations produce the same resulting potential when direct comparisons of the potential parameters is not feasible.
- For a potential to be suitable for radiation studies, the extreme close-range interaction energies must be prohibitively repulsive while not being so large that the resulting force on the atoms will eject them from the system during integration.  The diatom_scan results provide a means of evaluating the close-range interactions.
- The smoothness of the potential is also reflected in the diatom_scan energy results.  Numerical derivatives of the measured points can determine the order of smoothness as well as the approximate r values where discontinuities occur.
- Evaluating large separation values provides a means of identifying the energy of the isolated atoms, given that the separation exceeds the potential's cutoff.  The isolated_atom calculation is an alternative method for obtaining this.
