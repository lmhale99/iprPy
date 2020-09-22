## Method and Theory

The calculation loops over all symbol models of the potential and creates a system with a single particle inside a system with non-periodic boundary conditions.  The potential energy of each unique isolated atom is evaluated without relaxation/integration.

The cohesive energy, $E_{coh}$, of a crystal structure is given as the per-atom potential energy of the crystal structure at equilibrium $E_{crystal}/N$ relative to the potential energy of the same atoms infinitely far apart, $E_i^{\infty}$

$$ E_{coh} = \frac{E_{crystal} - \sum{N_i E_{i}^{\infty}}}{N},$$

Where the $N_i$ values are the number of each species $i$ and $\sum{N_i} = N$.

For most potentials, $E_i^{\infty}=0$ meaning that the measured potential energy directly corresponds to the cohesive energy.  However, this is not the case for all potentials as some have offsets either due to model artifacts or because it allowed for a better fitted model.
