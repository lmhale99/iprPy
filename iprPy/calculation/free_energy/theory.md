## Method and Theory

The calculation performs two different simulations: an nvt simulation to estimate Einstein solid spring constants for each atom type, and thermodynamic integrations from the selected interatomic potential to the Einstein solid model and back.  The method follows what is described in [Freitas, Asta, de Koning, Computational Materials Science 112 (2016) 333–341](https://doi.org/10.1016/j.commatsci.2015.10.050).

The Einstein solid spring constants, $k_i$, are evaluated using an nvt simulation run and measuring the mean squared displacements, $\left<\left( \Delta r_i \right)^2\right>$, averaged for each atom type $i$ and over time

$$ k_i = \frac{3 k_B T}{\left<\left( \Delta r_i \right)^2\right>} $$

The free energy integration works by first allowing the system to come to equilibrium with the target potential.  Next, "switching" steps are performed during which the interatomic potential gradually switches from the target potential to the reference potential. The system is then allowed to equilibrate using the reference potential before performing another switching stage back to the target potential.

Once the simulations are done, the measured Hamiltonian energy is integrated across the potential transformations allowing for the work of transformation to be estimated.  The work of transformation can then be added to the Gibbs free energy of the reference potential state to compute the absolute Gibbs free energy of the target potential state.