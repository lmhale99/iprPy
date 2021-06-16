## Method and Theory

The calculation method used here for computing elastic constants is based on the method used in the ELASTIC demonstration script created by Steve Plimpton and distributed with LAMMPS.

The math in this section uses Voigt notation, where indicies i,j correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are orthogonal box vectors.

A LAMMPS simulation performs thirteen energy/force minimizations

- One for relaxing the initial system.

- Twelve for relaxing systems in which a small strain of magnitude $\Delta \epsilon$ is applied to the system in both the positive and negative directions of the six Voigt strain components, $\pm \Delta \epsilon_{i}$.

The system virial pressures, $P_{i}$, are recorded for each of the thirteen relaxed configurations.  Two estimates for the $C_{ij}$ matrix for the system are obtained as

$$ C_{ij}^+ = - \frac{P_i(\Delta \epsilon_j) - P_i(0)}{\Delta \epsilon},$$

$$ C_{ij}^- = - \frac{P_i(0) - P_i(-\Delta \epsilon_j)}{\Delta \epsilon}.$$

The negative out front comes from the fact that the system-wide stress state is $\sigma_i = -P_i$.  A normalized, average estimate is also obtained by averaging the positive and negative strain estimates, as well as the symmetric components of the tensor

$$ C_{ij} = \frac{C_{ij}^+ + C_{ij}^- + C_{ji}^+ + C_{ji}^-}{4}.$$
