## Simulation design

The diffusion_liquid calculation performs multiple NVT MD simulations at a target temperature, with the only difference between the multiple stages/runs being what properties are computed.  The first optional stage is an equilibrium stage that allows for atomic velocities to equilibrate if the initial configuration is not already equilibrated. Multiple subsequent runs are then performed during which evaluations of the mean squared displacement (MSD) and the velocity auto-correlation function (VACF) are reset at the beginning of each smaller run. Final analysis provides three estimates of the diffusion constant: MSD long being the MSD estimate for the entire simulation time (post equilibration stage), MSD short being the averaged MSD estimates from the individual short runs, and VACF being the averaged VACF estimates from the individual short runs.

## MSD estimates

The MSD of all atoms in the system gives an averaged metric for how far atoms on average diffuse during a given time period. LAMMPS computes this value at every outputted timestep by evaluating $\left<Δr^2\right>$ for $Δr$ values relative to the timestep where the compute was started, and averaged over all atoms in the system. Once MSD is computed as a function of Δt, the diffusion constant can be evaluated using

$$ D = \frac{\left< Δr^2 \right>}{2dΔt},$$ 

where d is the number of dimensions included. Using this equation, D is typically estimated through a linear fit to compute the slope between the MSD and Δt.  When computing the linear fit, the beginning of the MSD curve is excluded (default is 400 timesteps) as the arbitrary reference configuration can skew the initial MSD values.

### Long MSD vs. short MSD

This calculation provides two estimates of the diffusion constant based on MSD values: long MSD and short MSD.  For long MSD, $\left<Δr^2\right>$ is computed across the full cumulative simulation time. For short MSD, $\left<Δr^2\right>$ is computed for each short simulation time, then a mean curve is obtained by averaging MSD values for the same Δt across all short runs.  This effectively allows for the $\left<Δr^2\right>$ values to be averaged over more samples thereby likely providing a better more consistent MSD vs Δt curve.

### VACF

The LAMMPS compute vacf method evaluates the VACF at every outputted timestep by evaluating $\left<v_0 ⋅ v_t\right>$ averaged over all atoms using $v_0$ values obtained at the timestep when the compute was started. Estimates for the diffusion constant can be obtained by integrating the VACF as a function of time.

$$ D = \frac{1}{d}\int_0^\infty{\left<v_0 ⋅ v_t\right>dt}, $$

where d is the number of dimensions included.

For the integral to converge to a finite value, the VACF is expected to quickly drop to 0.0. However, when you run simulations the VACF is typically found to fluctuate around a constant value (close to but not always zero) at large Δt. This can be reduced by increasing the number of samples being averaged, i.e. increasing the number of atoms and/or adding additional VACF measurements for the same Δt values.  This calculation does the second option by resetting the VACF calculation at the beginning of each short simulation run. 
 