## Method and Theory

The math in this section uses Voigt notation, where indicies i,j correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are orthogonal box vectors.

An initial system (and corresponding unit cell system) is supplied with box dimensions, ``$a_i^0$``, close to the equilibrium values. A LAMMPS simulation is performed that evaluates the system's pressures, ``$P_{i}$``, for the initial system as given, and subjected to twelve different strain states corresponding to one of ``$\epsilon_{i}$`` being given a value of ``$\frac{\Delta \epsilon}{2}$``, where ``$\Delta \epsilon$`` is the strain range parameter. Using the ``$P_{i}$`` values obtained from the strained states, the ``$C_{ij}$`` matrix for the system is estimated as

$$ C_{ij} \approx - \frac{P_i(\epsilon_j=\frac{\Delta \epsilon}{2}) - P_i(\epsilon_j=-\frac{\Delta \epsilon}{2})}{\Delta \epsilon}.$$

The negative out front comes from the fact that the system-wide stress state is ``$\sigma_i = -P_i$``. Using ``$C_{ij}$``, an attempt is made to compute the elastic compliance matrix as ``$S_{ij} = C_{ij}^{-1}$``. If successful, new box dimensions are estimated using ``$S_{ij}$``, ``$a_i^0$``, and ``$P_i$`` for the unstrained system 

$$ a_i = \frac{a_i^0}{1 - (\sum_{j=1}^3{S_{ij} P_j})}.$$

The system is updated using the new box dimensions. The process is repeated until either ``$a_i$`` converge less than a specified tolerance, ``$a_i$`` diverge from ``$a_i^0$`` greater than some limit, or convergence is not reached after 100 iterations. If the calculation is successful, the final ``$a_i$`` and corresponding ``$C_{ij}$`` are reported.