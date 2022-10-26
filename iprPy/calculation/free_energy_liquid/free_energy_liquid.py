# coding: utf-8

# Python script created by Lucas Hale

# Standard library imports
import random
from typing import Optional, Union

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate, aslist

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# iprPy imports
from ...tools import read_calc_file
from .UhlenbeckFordModel import UhlenbeckFordModel

def free_energy_liquid(lammps_command: str,
                       system: am.System,
                       potential: lmp.Potential,
                       temperature: float,
                       mpi_command: Optional[str] = None,
                       p: int = 50,
                       sigma: float = 1.5,
                       equilsteps: int = 25000,
                       switchsteps: int = 50000,
                       pressure: float = 0.0,
                       createvelocities: bool = True,
                       randomseed: Optional[int] = None) -> dict:
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
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

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    timestep = lmp.style.timestep(potential.units)

    # Build Uhlenbeck-Ford solution
    ufm = UhlenbeckFordModel(sigma=sigma, p=p, temperature=temperature,
                             volume=system.box.volume, natoms=system.natoms)

    if randomseed is None:
        randomseed = random.randint(1, 900000000)

    # Define lammps variables
    lammps_variables = {}
    
    # Dump initial system as data and build LAMMPS inputs
    system_info = system.dump('atom_data', f='init.dat',
                              potential=potential)

    # Modify pair_info into a hybrid/scaled with ufm
    if potential.pair_style in ['hybrid', 'hybrid/overlay']:
        system_info, pair_styles = modify_hybrid_pair_info_ufm(system_info, ufm,
                                                               energy_unit=lammps_units['energy'],
                                                               length_unit=lammps_units['length'])
    elif potential.pair_style == 'hybrid/scaled':
        raise ValueError('calculation does not yet support hybrid/scaled potentials')
    else:
        system_info, pair_styles = modify_pair_info_ufm(system_info, ufm,
                                                        energy_unit=lammps_units['energy'],
                                                        length_unit=lammps_units['length'])

    lammps_variables['atomman_system_pair_info'] = system_info

    # Build compute pair line(s)
    compute_pair = ''
    for i in range(len(pair_styles)):
        compute_pair += f'compute E_pair_{i+1} all pair {pair_styles[i]}\n'
    compute_pair += 'variable E_pair equal c_E_pair_1'
    for i in range(1, len(pair_styles)):
        compute_pair += f'+c_E_pair_{i+1}'
    lammps_variables['compute_pair'] = compute_pair

    # Create new velocities or not
    if createvelocities:
        lammps_variables['create_velocities'] = f'velocity all create {temperature} {randomseed} mom yes rot yes dist gaussian'
    else:
        lammps_variables['create_velocities'] = ''

    # Other run settings
    lammps_variables['timestep'] = timestep
    lammps_variables['switchsteps'] = switchsteps
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['temperature'] = temperature
    lammps_variables['temperature_damp'] = 100 * timestep
    lammps_variables['randomseed'] = randomseed
    
    # Write lammps input script
    lammps_script = 'free_energy_liquid.in'
    template = read_calc_file('iprPy.calculation.free_energy_liquid',
                              'free_energy_liquid.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps 
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
    
    # Extract LAMMPS thermo data for the switching runs.
    hamil_forward = np.loadtxt('forward_switch.txt', skiprows=1)
    hamil_reverse = np.loadtxt('reverse_switch.txt', skiprows=1)

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

def modify_pair_info_ufm(pair_info, ufm, energy_unit='eV', length_unit='angstrom'):
    """Transforms pair_info for a potential into a hybrid/scaled with ufm for thermodynamic integration"""
    newlines = []
    
    for line in pair_info.split('\n'):
        terms = line.split()
        
        if len(terms) > 0 and terms[0] == 'pair_style':
            # Extract original pair style
            pair_style = terms[1]
            pair_style_coeff = ' '.join(terms[1:])
            
            # Construct hybrid pair style
            newlines.append(f'pair_style hybrid/scaled v_nlambda {pair_style_coeff} v_lambda ufm 7.5')
            
            # Add pair_coeff for ufm
            epsilon = uc.get_in_units(ufm.epsilon, energy_unit)
            sigma = uc.get_in_units(ufm.sigma, length_unit)
            newlines.append(f'pair_coeff * * ufm {epsilon} {sigma}')
            
        elif len(terms) > 0 and terms[0] == 'pair_coeff':
            terms.insert(3, pair_style)
            newlines.append(' '.join(terms))
            
        else:
            newlines.append(line)
    
    return '\n'.join(newlines), [pair_style]

def modify_hybrid_pair_info_ufm(pair_info, ufm, energy_unit='eV', length_unit='angstrom'):
    newlines = []
    for line in pair_info.split('\n'):
        terms = line.split()

        if len(terms) > 0 and terms[0] == 'pair_style':
            pair_styles = []
            newline = 'pair_style hybrid/scaled'
            s = 2
            for e in range(3, len(terms)):
                try:
                    float(terms[e])
                except:
                    pair_styles.append(terms[s])
                    newline += f' v_nlambda {" ".join(terms[s:e])}'
                    s=e
            pair_styles.append(terms[s])
            newline += f' v_nlambda {" ".join(terms[s:e+1])} v_lambda ufm 7.5'
            newlines.append(newline)

            # Add pair_coeff for ufm
            epsilon = uc.get_in_units(ufm.epsilon, energy_unit)
            sigma = uc.get_in_units(ufm.sigma, length_unit)
            newlines.append(f'pair_coeff * * ufm {epsilon} {sigma}')
    
        else:
            newlines.append(line)
    
    return '\n'.join(newlines), pair_styles
    