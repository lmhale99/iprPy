## Theory

This calculation uses the LAMMPS compute heat/flux command to estimate the thermal conductivity of a system using the equilibrium Green-Kubo method.

The compute heat/flux command computes the heat flux $J$ using the equation

$$ \mathbf{J} = \frac{1}{V} \left[ \sum_i{e_i v_i} - \sum_i{S_i v_i}\right], $$

where $e_i$ is the per-atom energy (potential and kinetic), $v_i$ is the per-atom velocity, and $S_i$ is the per-atom stress tensor.

The command allows for the specification of computes for the per-atom kinetic energies, potential energies, and stress tensors. The kinetic and potential energies are usually the normal values computed for a potential, while the stress tensors can be computed with either "compute stress/atom" or "compute centroid/stress/atom".  The documentation states that normally only the virial component of the stress (and not the kinetic component) should be used. As for the two alternate stress computes, the LAMMPS documentation states that compute centroid/stress/atom should be used for angle, dihedral, improper and constraint force contributions as the regular compute stress/atom produces unphysical heat/flux values.

The thermal conductivity $\kappa$ can then be computed from the auto-correlation of the heat capacity

$$ \kappa = \frac{V}{k_BT^2} \int_0^{\infty}{\left< J_x\left( 0 \right) J_x\left( t \right)\right>dt} = \frac{V}{3k_BT^2} \int_0^{\infty}{\left< \mathbf{J}\left( 0 \right) \cdot \mathbf{J}\left( t \right)\right>dt}$$

The auto-correlation integrals can be estimated by numerically integrating from the measured heat flux values.