## Method and Theory

The math in this section uses Voigt notation, where indicies i,j correspond to 1=xx, 2=yy, 3=zz, 4=yz, 5=xz, and 6=xy, and x, y and z are orthogonal box vectors.

An initial system (and corresponding unit cell system) is supplied with box dimensions, ``$a_i^0$``, close to the equilibrium values. A LAMMPS simulation performs an energy/force minimization with a fix box_relax option to relax both the local atomic coordinates and the system's dimensions. The pressures, ``$P_{i}$``, of the relaxed state are recorded.

Further energy/force minimizations are then performed without box_relax to evaluate ``$P_{i}$`` at twelve different strain states corresponding to one of ``$\epsilon_{i}$`` being given a value of ``$\pm \Delta \epsilon$``, where ``$\Delta \epsilon$`` is the strain range parameter. Using the ``$P_{i}$`` values obtained from the strained states, the ``$C_{ij}$`` matrix for the system is estimated as

$$ C_{ij} \approx \frac{C_{ij}^+ + C_{ij}^-}{2}, $$

where

$$ C_{ij}^+ = - \frac{P_i(\epsilon_j=\Delta \epsilon) - P_i(\epsilon_j=0)}{\Delta \epsilon}.$$

$$ C_{ij}^- = - \frac{P_i(\epsilon_j=0) - P_i(\epsilon_j=-\Delta \epsilon)}{\Delta \epsilon}.$$

The negative out front comes from the fact that the system-wide stress state is ``$\sigma_i = -P_i$``. 

The full process is repeated until the box dimensions from one iteration to the next are within the specified relative convergence tolerance.