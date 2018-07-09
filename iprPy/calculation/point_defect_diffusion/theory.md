## Method and Theory

First, a defect system is constructed by adding a single point defect (or
defect cluster) to an initially bulk system using the atomman.defect.point()
function.

A LAMMPS simulation is then performed on the defect system.  The simulation
consists of two separate runs

1. NVT equilibrium run: The system is allowed to equilibrate at the given
   temperature using nvt integration.
 
2. NVE measurement run: The system is then evolved using nve integration, and
   the total mean square displacement of all atoms is measured as a function
   of time.

Between the two runs, the atomic velocities are rescaled such that the average
temperature of the nve run is closer to the target temperature.

The mean square displacement of the defect, $\left< \Delta r_{ptd}^2 \right>$
is then estimated using the mean square displacement of the atoms 
$\left< \Delta r_{i}^2 \right>$.  Under the assumption that all diffusion is
associated with the single point defect, the defect's mean square displacement
can be taken as the summed square displacement of the atoms

$$ \left< \Delta r_{ptd}^2 \right> \approx \sum_i^N \Delta r_{i}^2 = N \left< \Delta r_{i}^2 \right> $$,

where $N$ is the number of atoms in the system.  The diffusion constant is
then estimated by linearly fitting the change in mean square displacement with
time

$$ \left< \Delta r_{ptd}^2 \right> = 2 d D_{ptd} \Delta t $$,

where d is the number of dimensions included.