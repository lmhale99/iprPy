## Method and Theory

This calculation method uses the [deformation–fluctuation hybrid method](https://doi.org/10.1016/j.cpc.2011.09.006) for computing elastic constants as implemented in LAMMPS under the [compute born/matrix numdiff](https://docs.lammps.org/compute_born_matrix.html) command.

With the fluctuation method, the elastic constants can be estimated by computing three terms:

$$ C_{ij} = C_{ij}^{Born} + C_{ij}^{fluc} + C_{ij}^{kin}$$

$C_{ij}^{Born}$ is the mean of the Born matrix, which is the second derivatives of the potential energy with respect to strain

$$ C_{ij}^B=\left<\frac{1}{V} \frac{\partial^2U}{\partial\epsilon_i\partial\epsilon_j} \right>$$

The LAMMPS compute born/matrix command evaluates this matrix as the simulation runs.  For the numdiff option, the calculation follows the deformation-fluctuation method and uses finite differences of the energy to approximate the derivatives.  This is done by the calculation applying linear strain fields to all atoms in the system associated with all six independent $\epsilon_{ij}$ components in positive and negative directions allowing for an estimate of the second derivative wrt to the strains. This makes this calculation available to any interatomic potential that evaluates energies but does add a dependency of the calculation on the size of the strain used.

$C_{ij}^{fluc}$ is the fluctuation (a.k.a. stress) matrix given by

$$ - \frac{V}{k_B T} \left( \left<\sigma_i \sigma_j \right> - \left<\sigma_i\right> \left<\sigma_j\right> \right), $$

where $\sigma$ is the virial stress tensor.  Note that sometimes the fluctuation term is defined without the negative included and is then subtracted from the other terms when computing $C_{ij}$.  This term is computed by regularly measuring the virial pressure of the system during the LAMMPS calculation, then computing the covariance of the values.

$C_{ij}^{kin}$ is the kinetic term, which is the "ideal gas" contribution and only depends on temperature 

 $$ C_{ij}^{kin} = \frac{N k_B T}{V} ( \delta_{ij} + (\delta_{1i} + \delta_{2i} + \delta_{3i}) * (\delta_{1j} + \delta_{2j} + \delta_{3j}) ), $$
    
where δ is the Kronecker delta. Evaluating the second part of the term, this can be simplified to
    
 $$ C_{ij}^{kin} = \frac{N k_B T}{V} \Delta_{ij}, $$
    
where $\Delta_{ij} = 2$ for $ij =11, 22, 33$, $\Delta_{ij} = 1$ for $ij = 44, 55, 66$ and $\Delta_{ij} = 0$ otherwise.    

