# coding: utf-8

# Python script created by Lucas Hale
from datetime import date
from typing import Optional
import random

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def elastic_constants_dynamic(lammps_command: str,
                              system: am.System,
                              potential: lmp.Potential,
                              temperature: float,
                              mpi_command: Optional[str] = None,
                              ucell: Optional[am.System] = None,
                              normalized_as: str = 'triclinic',
                              strainrange: float = 1e-6,
                              equilsteps: int = 20000,
                              runsteps: int = 200000,
                              thermosteps: int = 100,
                              randomseed: Optional[int] = None
                              ) -> dict:
    """
    Computes elastic constants for a system during dynamic simulations using
    the LAMMPS compute born/matrix method.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to run the calculation at.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    normalized_as : str, optional
        This allows for the computed elastic constants matrix values to be
        normalized to the symmetries expected for a specified crystal family.
        Default value of 'triclinic' will perform no normalization.
    strainrange : float, optional
        The magnitude of strains to use to generate finite difference
        approximations for the exact virial stress.  Picking a good value may
        be dependent on the crystal structure and it is recommended to try
        multiple different values.  Default value is 1e-6.
    equilsteps : int, optional
        Number of integration steps to perform prior to performing the
        born/matrix calculation to equilibrate the system.  Default value is
        20000.
    runsteps : int, optional
        Number of integration steps to perform during the born/matrix
        calculation.  Default value is 200000.
    thermosteps : int, optional
        How often to output thermo values to sample the computed stress and
        born/matrix values.
    randomseed : int or None, optional
        A random number seed between 1 and 9000000 to use for initializing
        velocities and use with the langevin thermostat.  Default value of None
        will pick a random value.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        - **'measured_pressure'** (*float*) - The mean measured pressure of the
          system.
        - **'Cij_born'** (*numpy.ndarray*) - The 6x6 tensor of the Born
          component of the Cij calculation.
        - **'Cij_fluc'** (*numpy.ndarray*) - The 6x6 tensor of the fluctuation
          component of the Cij calculation.
        - **'Cij_kin'** (*numpy.ndarray*) - The 6x6 tensor of the kinetic
          component of the Cij calculation.
        - **'C'** (*atomman.ElasticConstants*) - The computed elastic constants
          obtained from averaging the negative and positive strain values.
    """
    # Convert hexagonal cells to orthorhombic to avoid LAMMPS tilt issues
    #if am.tools.ishexagonal(system.box):
    #    system = system.rotate([[2,-1,-1,0], [0, 1, -1, 0], [0,0,0,1]])
    
    # Set randomseed
    if randomseed is None: 
        randomseed = random.randint(1, 900000000)
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']

    # Check for compatibility
    if lammps_date < date(2022, 5, 4):
        raise ValueError('LAMMPS from May 4, 2022 or newer required for the born/matrix calculation')
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat', potential=potential)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['temperature'] = temperature
    lammps_variables['strainrange'] = strainrange
    lammps_variables['equilsteps'] = equilsteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['randomseed'] = randomseed
    
    timestep = lmp.style.timestep(potential.units)
    lammps_variables['timestep'] = timestep
    
    # Fill in template files
    lammps_script = 'born_matrix.in'
    template = read_calc_file('iprPy.calculation.elastic_constants_dynamic',
                              'born_matrix.template')
    with open(lammps_script, 'w') as f:
        f.write(filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, script_name=lammps_script,
                     mpi_command=mpi_command, screen=False)
        
    # Extract thermo data
    thermo = output.simulations[1].thermo
    
    # Compute the different components of the Cij expression from thermo data
    Cij_born = build_Cij_born(thermo, system.box.volume, lammps_units)
    Cij_fluc = build_Cij_fluc(thermo, system.natoms, temperature,
                              system.box.volume, lammps_units)
    Cij_kin = build_Cij_kin(system.natoms, temperature, system.box.volume)
    
    C = am.ElasticConstants(Cij = Cij_born + Cij_fluc + Cij_kin).normalized_as(normalized_as)
    
    pressure = uc.set_in_units(thermo.Press.mean(), lammps_units['pressure'])
    
    results_dict = {}
    results_dict['measured_pressure'] = pressure
    results_dict['Cij_born'] = Cij_born
    results_dict['Cij_fluc'] = Cij_fluc
    results_dict['Cij_kin'] = Cij_kin
    results_dict['C'] = C
    
    return results_dict
    
def build_Cij_born(thermo, V, lammps_units):
    """
    Constructs the Born component of the Cij calculation from the LAMMPS thermo
    outputs.  The LAMMPS born/matrix outputs are the second derivatives of
    energy wrt strains.  
    
        Cij_born = 1 / V * ( ∂2U / (∂ϵ_i ∂ϵ_j) ) 
    """
    
    # Construct du2 matrix from mean LAMMPS outputs
    du2 = np.empty((6,6))
    du2[0,0] = thermo['c_born[1]'].mean()
    du2[1,1] = thermo['c_born[2]'].mean()
    du2[2,2] = thermo['c_born[3]'].mean()
    du2[3,3] = thermo['c_born[4]'].mean()
    du2[4,4] = thermo['c_born[5]'].mean()
    du2[5,5] = thermo['c_born[6]'].mean()
    du2[0,1] = du2[1,0] = thermo['c_born[7]'].mean()
    du2[0,2] = du2[2,0] = thermo['c_born[8]'].mean()
    du2[0,3] = du2[3,0] = thermo['c_born[9]'].mean()
    du2[0,4] = du2[4,0] = thermo['c_born[10]'].mean()
    du2[0,5] = du2[5,0] = thermo['c_born[11]'].mean()
    du2[1,2] = du2[2,1] = thermo['c_born[12]'].mean()
    du2[1,3] = du2[3,1] = thermo['c_born[13]'].mean()
    du2[1,4] = du2[4,1] = thermo['c_born[14]'].mean()
    du2[1,5] = du2[5,1] = thermo['c_born[15]'].mean()
    du2[2,3] = du2[3,2] = thermo['c_born[16]'].mean()
    du2[2,4] = du2[4,2] = thermo['c_born[17]'].mean()
    du2[2,5] = du2[5,2] = thermo['c_born[18]'].mean()
    du2[3,4] = du2[4,3] = thermo['c_born[19]'].mean()
    du2[3,5] = du2[5,3] = thermo['c_born[20]'].mean()
    du2[4,5] = du2[5,4] = thermo['c_born[21]'].mean()
    du2 = uc.set_in_units(du2, lammps_units['energy'])
    
    # Divide by volume
    return du2 / V
    
def build_Cij_fluc(thermo, N, T, V, lammps_units):
    """
    Constructs the fluctuation component of the Cij calculation from the LAMMPS
    stress (i.e. pressure) outputs.
    
        C_fluc = - V / (kB T) * ( <σ_i σ_j> - <σ_i> <σ_j> )
    """
    # Switch for 0K
    if T == 0:
        return np.zeros((6,6))
    
    # Extract the virial contributions to the stress tensor 
    σ = uc.set_in_units(np.array([
        -thermo['c_virial[1]'].values,
        -thermo['c_virial[2]'].values,
        -thermo['c_virial[3]'].values,
        -thermo['c_virial[4]'].values,
        -thermo['c_virial[5]'].values,
        -thermo['c_virial[6]'].values]), lammps_units['pressure'])

    # Compute the virial stress fluctuation term
    # cov == (<σ_i σ_j> - <σ_i> <σ_j>)
    fluc = np.cov(σ)
    
    # Multipy by V / (kb T) 
    kB = uc.unit['kB']
    return - (V / (kB * T)) * fluc
    
def build_Cij_kin(N, T, V):
    """
    Constructs the kinetic component of the Cij calculation.
    
    C_kin = ( (N kB T) / V ) ( δ_ij + (δ_1i + δ_2i + δ_3i) * (δ_1j + δ_2j + δ_3j) )
    
    where δ is the Kronecker delta. Evaluating the second part of the term, this
    can be simplified to
    
    C_kin = ( (N kB T) / V ) Δ_ij
    
    where Δ_ij = 2 for i = j = (1,2,3), Δ_ij = 1 for i = j = (4,5,6) and Δ_ij = 0
    otherwise.    
    """
    
    # Build delta matrix
    Δ = np.zeros((6,6))
    Δ[0,0] = Δ[1,1] = Δ[2,2] = 2
    Δ[3,3] = Δ[4,4] = Δ[5,5] = 1
    
    kB = uc.unit['kB']
    return Δ * N * kB * T / V
