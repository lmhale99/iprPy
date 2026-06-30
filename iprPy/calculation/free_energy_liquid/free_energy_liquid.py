# Python script created by Lucas Hale

# Standard library imports
from typing import Optional, Union

from potentials.record.PotentialLAMMPS import PotentialLAMMPS

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.unitconvert as uc
from atomman.typing import lammpspotential, unitfloat
from atomman.lammps import LAMMPS, LAMMPSobj
from atomman.tools import aslist
from atomman.thermo import UhlenbeckFordModel

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

def free_energy_liquid(lammps_command: Union[str, LAMMPSobj],
                       system: am.System,
                       potential: lammpspotential,
                       temperature: float,
                       mpi_command: Optional[str] = None,
                       p: int = 50,
                       sigma: float = 1.5,
                       equilsteps: int = 25000,
                       switchsteps: int = 50000,
                       pressure: unitfloat = 0.0,
                       createvelocities: bool = True,
                       randomseed: Optional[int] = None,
                       usefiles: bool = False) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
    Parameters
    ----------
    lammps_command : str, LAMMPSEXE or LAMMPSLIB
        LAMMPS executable command, LAMMPS library name, or an atomman LAMMPS
        interface object.
    system : atomman.System
        The system to perform the calculation on.
    potential : PotentialLAMMPS or PotentialLAMMPSKIM
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to run at.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    p : int, optional
        The Uhlenbeck-Ford energy scale multiplier.  Allowed values are 1, 25,
        50, 75, and 100.  Default value is 50.
    sigma : float, optional
        The Uhlenbeck-Ford length scale parameter.  Default value is 1.5.
    equilsteps : int, optional
        The number of equilibration timesteps at the beginning of simulations
        to ignore before evaluations.  This is used before each thermo switch
        run.  Default value is 25000.
    switchsteps : int, optional
        The number of integration steps to perform during each of the two
        switch runs.  Default value is 50000.
    pressure : float, optional
        A value of pressure to use for computing the Gibbs free energy from
        the Helmholtz free energy.  NOTE: this is not used to equilibrate the
        system during this calculation!  Default value is 0.0.
    randomseed : int or None, optional
        Random number seed used by LAMMPS.  Default is None which will select
        a random int between 1 and 900000000.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'work_forward'** (*float*) - The work/atom during the
          forward switching step.
        - **'work_reverse'** (*float*) - The work/atom during the
          reverse switching step.
        - **'work'** (*float*) - The reversible work/atom.
        - **'Helmholtz_reference'** (*float*) - The Helmholtz free energy/atom
          for the reference Einstein solid.
        - **'Helmholtz'** (*float*) - The Helmholtz free energy/atom.
        - **'Gibbs'** (*float*) - The Gibbs free energy/atom.
    """
    # Create a LAMMPS object if needed
    lmp = LAMMPS(lammps_command, mpi_command=mpi_command, potential=potential)

    # Convert values given with units if needed
    pressure = uc.set_in_units(pressure)

    # Set randomseed
    randomseed = am.lammps.seed(randomseed)

    # Build Uhlenbeck-Ford solution
    ufm = UhlenbeckFordModel(sigma=sigma, p=p, temperature=temperature,
                             volume=system.box.volume, natoms=system.natoms)

    # Create a UFM potential object
    pot_ufm = PotentialLAMMPS(pair_style='ufm', atoms=potential.atoms)
    pot_ufm.pair_style_terms.add_term('parameter', uc.get_in_units(7.5, lmp.unitsdict['length']))
    pot_ufm.add_pair_coeff()
    pot_ufm.pair_coeffs[0].add_term('parameter', uc.get_in_units(ufm.epsilon, lmp.unitsdict['energy']))
    pot_ufm.pair_coeffs[0].add_term('parameter', uc.get_in_units(sigma, lmp.unitsdict['length']))

    # Create a hybrid/scaled potential between the given potential and the UFM one
    scalars = ['v_nlambda', 'v_lambda']
    hybrid_potential = PotentialLAMMPS.hybrid([potential, pot_ufm],
                                               pair_style='hybrid/scaled',
                                               scalars=scalars)
    
    # Update lmp object's potential to be the hybrid
    lmp.potential = hybrid_potential

    # Run thermodynamic integration simulation
    thermodynamic_integration(lmp, system, temperature,
                              equilsteps, switchsteps, createvelocities,
                              randomseed, usefiles)

    # Extract LAMMPS thermo data for the switching runs.
    hamil_forward = uc.set_in_units(np.loadtxt('forward_switch.txt', skiprows=1),
                                    lmp.unitsdict['energy'])
    hamil_reverse = uc.set_in_units(np.loadtxt('reverse_switch.txt', skiprows=1),
                                    lmp.unitsdict['energy'])


    # Integrate the Hamiltonians to compute the switching work
    work_forward, work_reverse, work = integrate_for_work(hamil_forward,
                                                          hamil_reverse)

    # Get values per atype for computing the ideal gas free energy reference
    natoms_atype = []
    for i in range(system.natypes):
        natoms_atype.append(np.sum(system.atoms.atype == i+1))
    masses = potential.masses(system.symbols)
    volume = system.box.volume

    # Evaluate the reference free energy
    F_ufm = ufm.free_energy() * system.natoms
    F_ig = ideal_gas_free_energy(temperature, volume, masses, natoms_atype)

    # Compute the Helmholtz free energy of the system
    F_sys = F_ig + F_ufm + work

    # Compute the Gibbs free energy of the system
    G_sys = F_sys + pressure * volume

    results = {}
    results['work_forward'] = work_forward / system.natoms
    results['work_reverse'] = work_reverse / system.natoms
    results['work'] = work / system.natoms
    results['Helmholtz_reference'] = (F_ufm + F_ig) / system.natoms
    results['Helmholtz'] = F_sys / system.natoms
    results['Gibbs'] = G_sys / system.natoms
    
    return results





def thermodynamic_integration(lmp: LAMMPSobj,
                              system: am.System,
                              temperature: float,
                              equilsteps: int,
                              switchsteps: int,
                              createvelocities: bool,
                              randomseed: int,
                              usefiles: bool):
    logfile = 'log_ti.lammps'
    if usefiles:
        script = 'free_energy_liquid.in'
    else:
        script = None

    # Search potential pair_info to identify included pair styles
    pair_styles = []
    terms = lmp.potential.pair_info(comments=False).split()
    for i, term in enumerate(terms):
        if term in ['v_nlambda']:
            pair_styles.append(terms[i+1])

    # Define lambda factors
    lmp.cmd.variable('tau', 'equal', 0.0)
    lmp.cmd.variable('lambda', 'equal', 'v_tau^5*(70*v_tau^4-315*v_tau^3+540*v_tau^2-420*v_tau+126)')
    lmp.cmd.variable('nlambda', 'equal', '1-v_lambda')

    # Timestep and timestep-dependent variables
    timestep = am.lammps.style.timestep(lmp.potential.units)
    temperature_damp = 100 * timestep

    # Pass system and potential info into LAMMPS
    lmp.new_system_from_data_file(system, filename='init.dat', tilt_large=True,
                                  usefiles=usefiles, logfile=logfile)
    
    lmp.cmd.timestep(timestep)
    lmp.cmd.variable('pe', 'equal', 'pe')

    if createvelocities:
        lmp.commands_string('\n# Create velocities')
        lmp.cmd.velocity('all', 'create', temperature, randomseed,
                         'mom', 'yes', 'rot', 'yes', 'dist', 'gaussian')
        
    lmp.cmd.compute('E_ufm', 'all', 'pair', 'ufm')
    
    E_pair = []
    for i in range(len(pair_styles)):
        lmp.cmd.compute(f'E_pair_{i+1}', 'all', 'pair', f'{pair_styles[i]}')
        E_pair.append(f'c_E_pair_{i+1}')
    lmp.cmd.variable('E_pair', 'equal', '+'.join(E_pair))
    lmp.cmd.variable('hamil', 'equal', 'v_E_pair-c_E_ufm')


    lmp.cmd.fix('nve', 'all', 'nve')
    lmp.cmd.fix('langevin', 'all', 'langevin',
                temperature, temperature, temperature_damp, randomseed, 'zero', 'yes')
    lmp.cmd.compute('temp_com', 'all', 'temp/com')
    lmp.cmd.fix_modify('langevin', 'temp', 'temp_com')

    lmp.cmd.thermo(100)
    lmp.cmd.thermo_style('custom', 'step', 'c_temp_com', 'pe', 'ke', 'etotal',
                         'v_E_pair', 'c_E_ufm', 'v_lambda')

    lmp.cmd.run(equilsteps)

    # Run forward integration
    lmp.cmd.variable('tau', 'equal', 'ramp(0.0,1.0)')
    lmp.cmd.fix('forward_switch', 'all', 'print', 1, '"${hamil}"',
                'screen', 'no', 'file', 'forward_switch.txt')
    lmp.cmd.run(switchsteps)
    lmp.cmd.unfix('forward_switch')

    # Equilibrate for pure ufm
    lmp.cmd.variable('tau', 'equal', 1.0)
    lmp.cmd.run(equilsteps)

    # Run reverse integration
    lmp.cmd.variable('tau', 'equal', 'ramp(1.0,0.0)')
    lmp.cmd.fix('reverse_switch', 'all', 'print', 1, '"${hamil}"',
                'screen', 'no', 'file', 'reverse_switch.txt')
    lmp.cmd.run(switchsteps)
    lmp.cmd.unfix('reverse_switch')

    # Run EXE, get log output
    log = lmp.end_and_get_log(script)

def ideal_gas_free_energy(temperature, volume, masses, natoms):
    """
    Get the free energy of an ideal gas
    
    Parameters
    ----------
    temperature : float
        The temperature to use.
    volume : float
        The total volume of the system.
    masses : float or list
        The atomic masses for each atom type.
    natoms : float or list
        The number of atoms for each atom type.
    
    Returns
    -------
    float
        Computed free energy of the ideal gas.
    """
    # Get constants
    Na = uc.unit['NA']
    kB = uc.unit['kB']
    h = uc.unit['hPlanck']
    π = np.pi
    
    # Remap inputs for the equations
    T = temperature
    V = volume
    m = np.array(aslist(masses))
    N = np.array(aslist(natoms))

    # Compute de Broglie thermal wavelength
    Λ = (h**2 / (2 * π * kB * T * m)) ** 0.5
    
    # Compute numerical density
    ρ = N.sum() / V
    
    # Compute elemental concentrations
    c = N / N.sum()

    # Compute the free energy
    F = (N * kB * T * (np.log(ρ) + 3 * np.log(Λ) - 1 + np.log(c))).sum()
    return F

def integrate_for_work(hamil_forward, hamil_reverse):

    def Δλ(τ1, τ2):
        """Compute the change in λ between τ values"""
        return 70*(τ2**9-τ1**9) - 315*(τ2**8-τ1**8) + 540*(τ2**7-τ1**7) - 420*(τ2**6-τ1**6) + 126*(τ2**5-τ1**5)

    # Numerically compute the forward and reverse work using the trapezoidal rule and Δλ
    τ = np.linspace(0.0, 1.0, len(hamil_forward))
    work_forward = np.sum((hamil_forward[1:] + hamil_forward[:-1]) /2 * Δλ(τ[:-1], τ[1:]))
    
    τ = np.linspace(1.0, 0.0, len(hamil_reverse))
    work_reverse = np.sum((hamil_reverse[1:] + hamil_reverse[:-1]) /2 * Δλ(τ[:-1], τ[1:]))
    
    # Average difference for reversible work
    work = (work_forward - work_reverse) / 2

    return work_forward, work_reverse, work

