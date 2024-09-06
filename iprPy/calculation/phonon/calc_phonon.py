# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from pathlib import Path
from typing import Optional
import datetime

# http://www.numpy.org/
import numpy as np

import pandas as pd

# https://matplotlib.org/
import matplotlib.pyplot as plt

# https://atztogo.github.io/phonopy/phonopy-module.html
try:
    import phonopy
except ImportError:
    raise ImportError("The package, phonopy, is not installed by default. Please install with pip or conda.")

from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc
from atomman.tools import filltemplate

# iprPy imports
from ...tools import read_calc_file

def phonon_quasiharmonic(lammps_command: str,
                         ucell: am.System,
                         potential: lmp.Potential,
                         mpi_command: Optional[str] = None,
                         a_mult: int = 2,
                         b_mult: int = 2,
                         c_mult: int = 2,
                         distance: float = 0.01,
                         symprec: float = 1e-5,
                         strainrange: float = 0.01,
                         numstrains: int = 5) -> dict:
    """
    Function that performs phonon and quasiharmonic approximation calculations
    using phonopy and LAMMPS.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The unit cell system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    a_mult : int, optional
        The a size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    b_mult : int, optional
        The b size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    c_mult : int, optional
        The c size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    distance : float, optional
        The atomic displacement distance used for computing the phonons.
        Default value is 0.01.
    symprec : float, optional
        Absolute length tolerance to use in identifying symmetry of atomic
        sites and system boundaries. Default value is 1e-5.
    strainrange : float, optional
        The range of strains to apply to the unit cell to use with the
        quasiharmonic calculations.  Default value is 0.01.
    numstrains : int, optional
        The number of strains to use for the quasiharmonic calculations.
        Must be an odd integer.  If 1, then the quasiharmonic calculations
        will not be performed.  Default value is 5.
    """
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Convert ucell to a primitive cell
    ucell = ucell.dump('primitive_cell', symprec=symprec)

    # Get unstrained box vectors
    vects = ucell.box.vects

    # Generate the range of strains
    if numstrains == 1:
        zerostrain = phononcalc(lammps_command, ucell, potential,
                                mpi_command=mpi_command,
                                a_mult=a_mult, b_mult=b_mult, c_mult=c_mult,
                                distance=distance, symprec=symprec,
                                lammps_date=lammps_date)
        phonons = [zerostrain['phonon']]
        qha = None

    elif numstrains % 2 == 0 or numstrains < 5:
        raise ValueError('Invalid number of strains: must be odd and 1 or >= 5')
    else:
        strains = np.linspace(-strainrange, strainrange, numstrains)
        istrains = np.linspace(-(numstrains-1)/2, (numstrains-1)/2, numstrains, dtype=int)

        volumes = []
        energies = []
        phonons = []
        temperatures = None
        free_energy = None
        heat_capacity = None
        entropy = None

        # Loop over all strains
        for i in range(numstrains):
            strain = strains[i]
            if numstrains != 1:
                istrain = f'_{istrains[i]}'
            else:
                istrain = ''

            # Identify the zero strain run
            if istrains[i] == 0:
                zerostrainrun = True
            else:
                zerostrainrun = False
            
            # Generate system at the strain
            newvects = vects * (1 + strain)
            ucell.box_set(vects=newvects, scale=True)
            volumes.append(ucell.box.volume)
            system = ucell.supersize(a_mult, b_mult, c_mult)

            # Define lammps variables
            lammps_variables = {}
            system_info = system.dump('atom_data', f='disp.dat',
                                    potential=potential)
            lammps_variables['atomman_system_pair_info'] = system_info

            # Set dump_modify_format based on lammps_date
            if lammps_date < datetime.date(2016, 8, 3):
                lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e"'
            else:
                lammps_variables['dump_modify_format'] = 'float %.13e'

            # Write lammps input script
            lammps_script = 'phonon.in'
            template = read_calc_file('iprPy.calculation.phonon', 'phonon.template')
            with open(lammps_script, 'w') as f:
                f.write(filltemplate(template, lammps_variables, '<', '>'))

            # Run LAMMPS
            output = lmp.run(lammps_command, script_name='phonon.in',
                             mpi_command=mpi_command)

            # Extract system energy
            thermo = output.simulations[0]['thermo']
            energy = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])

            # Scale energy by sizemults and append to list
            energies.append(energy / (a_mult * b_mult * c_mult))

            # Compute phonon info for ucell
            phononinfo = phononcalc(lammps_command, ucell, potential, mpi_command=mpi_command,
                                    a_mult=a_mult, b_mult=b_mult, c_mult=c_mult,
                                    distance=distance, symprec=symprec, istrain=istrain,
                                    plot=zerostrainrun, lammps_date=lammps_date)
            phonons.append(phononinfo['phonon'])
            
            # Extract temperature values from the first run
            if temperatures is None:
                temperatures = phononinfo['thermal_properties']['temperatures']
                
                # Initialize QHA input arrays
                free_energy = np.empty((len(temperatures), len(strains)))
                heat_capacity = np.empty((len(temperatures), len(strains)))
                entropy = np.empty((len(temperatures), len(strains)))
            
            # Get values for zerostrainrun
            if zerostrainrun is True:
                zerostrain = phononinfo
            
            # Copy values to qha input arrays
            free_energy[:, i] = phononinfo['thermal_properties']['free_energy']
            entropy[:, i] = phononinfo['thermal_properties']['entropy']
            heat_capacity[:, i] = phononinfo['thermal_properties']['heat_capacity']
        
        # Try to compute qha
        try:
            eos = 'vinet'
            qha = phonopy.PhonopyQHA(volumes=volumes,
                        electronic_energies=energies,
                        temperatures=temperatures,
                        free_energy=free_energy,
                        cv=heat_capacity, eos=eos,
                        entropy=entropy)
        except:
            try:
                eos = 'birch_murnaghan'
                qha = phonopy.PhonopyQHA(volumes=volumes,
                        electronic_energies=energies,
                        temperatures=temperatures,
                        free_energy=free_energy,
                        cv=heat_capacity, eos=eos,
                        entropy=entropy)
            except:
                qha = None
    
    results = {}    
    
    # Add phonopy objects
    results['phonon_objects'] = phonons
    results['qha_object'] = qha
    
    # Extract zerostrain properties
    results['band_structure'] = zerostrain['band_structure']
    results['density_of_states'] = zerostrain['dos']

    # Convert units on thermal properties
    results['thermal_properties'] = zerostrain['thermal_properties']
    results['thermal_properties']['temperature'] = results['thermal_properties'].pop('temperatures')
    results['thermal_properties']['Helmholtz'] = uc.set_in_units(results['thermal_properties'].pop('free_energy'), 'kJ/mol')
    results['thermal_properties']['entropy'] = uc.set_in_units(results['thermal_properties'].pop('entropy'), 'J/K/mol')
    results['thermal_properties']['heat_capacity_v'] = uc.set_in_units(results['thermal_properties'].pop('heat_capacity'), 'J/K/mol')
    
    if qha is not None:

        results['qha_eos'] = eos

        # Create QHA plots
        qha.plot_bulk_modulus()
        plt.xlabel('Volume ($Å^3$)', size='large')
        plt.ylabel('Energy ($eV$)', size='large')
        plt.savefig('bulk_modulus.png', dpi=400, bbox_inches='tight')
        plt.close()

        qha.plot_helmholtz_volume()
        plt.savefig('helmholtz_volume.png', dpi=400)
        plt.close()

        # Package volume vs energy scans
        results['volume_scan'] = {}
        results['volume_scan']['volume'] = np.array(volumes)
        results['volume_scan']['strain'] = strains
        results['volume_scan']['energy'] = np.array(energies)
        
        # Compute and add QHA properties
        properties = qha.get_bulk_modulus_parameters()
        results['E0'] = uc.set_in_units(properties[0], 'eV')
        results['B0'] = uc.set_in_units(properties[1], 'eV/angstrom^3')
        results['B0prime'] = uc.set_in_units(properties[2], 'eV/angstrom^3')
        results['V0'] = uc.set_in_units(properties[3], 'angstrom^3')
        
        results['thermal_properties']['volume'] = uc.set_in_units(np.hstack([qha.volume_temperature, np.nan]), 'angstrom^3')
        results['thermal_properties']['thermal_expansion'] = np.hstack([qha.thermal_expansion, np.nan])
        results['thermal_properties']['Gibbs'] = uc.set_in_units(np.hstack([qha.gibbs_temperature, np.nan]), 'eV')
        results['thermal_properties']['bulk_modulus'] = uc.set_in_units(np.hstack([qha.bulk_modulus_temperature, np.nan]), 'GPa')
        results['thermal_properties']['heat_capacity_p_numerical'] = uc.set_in_units(np.hstack([qha.heat_capacity_P_numerical, np.nan]), 'J/K/mol')
        results['thermal_properties']['heat_capacity_p_polyfit'] = uc.set_in_units(np.hstack([qha.heat_capacity_P_polyfit, np.nan]), 'J/K/mol')
        results['thermal_properties']['gruneisen'] = np.hstack([qha.gruneisen_temperature, np.nan])
    
    # Build extra data files of results
    save_band_structure(results['band_structure'])
    save_density_of_states(results['density_of_states'])
    save_thermal_properties(results['thermal_properties'])

    return results


def phononcalc(lammps_command: str,
               ucell: am.System,
               potential: lmp.Potential,
               mpi_command: Optional[str] = None,
               a_mult: int = 2,
               b_mult: int = 2,
               c_mult: int = 2,
               distance: float = 0.01,
               symprec: float = 1e-5,
               istrain: str = '',
               plot: bool = True,
               lammps_date: Optional[datetime.date] = None) -> dict:
    """
    Uses phonopy to compute the phonons for a unit cell structure using a
    LAMMPS interatomic potential.

    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The unit cell system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    a_mult : int, optional
        The a size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    b_mult : int, optional
        The b size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    c_mult : int, optional
        The c size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 2.
    distance : float, optional
        The atomic displacement distance used for computing the phonons.
        Default value is 0.01.
    symprec : float, optional
        Absolute length tolerance to use in identifying symmetry of atomic
        sites and system boundaries. Default value is 1e-5.
    istrain: str, optional
        A string to add to saved yaml files to ensure their uniqueness for the
        different strains explored by QHA.  Default value is '', which assumes
        only one calculation is being performed.
    plot : bool, optional
        Flag indicating if band structure and DOS figures are to be generated.
        Default value is True.
    lammps_date : datetime.date, optional
        The version date associated with lammps_command.  If not given, the
        version will be identified.
    """
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    if lammps_date is None:
        lammps_date = lmp.checkversion(lammps_command)['date']
    
   # Convert ucell to a primitive cell
    ucell = ucell.dump('primitive_cell', symprec=symprec)
    
    # Initialize Phonopy object
    phonon = phonopy.Phonopy(ucell.dump('phonopy_Atoms', symbols=potential.elements(ucell.symbols)),
                             [[a_mult, 0, 0], [0, b_mult, 0], [0, 0, c_mult]],
                             factor=phonopy.units.VaspToTHz)
    phonon.generate_displacements(distance=distance)
    
    # Loop over displaced supercells to compute forces
    forcearrays = []
    for supercell in phonon.supercells_with_displacements:
        
        # Save to LAMMPS data file
        system = am.load('phonopy_Atoms', supercell, symbols=ucell.symbols)
        system_info = system.dump('atom_data', f='disp.dat',
                                  potential=potential)
        
        # Define lammps variables
        lammps_variables = {}
        lammps_variables['atomman_system_pair_info'] = system_info

        # Set dump_modify_format based on lammps_date
        if lammps_date < datetime.date(2016, 8, 3):
            lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e"'
        else:
            lammps_variables['dump_modify_format'] = 'float %.13e'

        # Write lammps input script
        lammps_script = 'phonon.in'
        template = read_calc_file('iprPy.calculation.phonon', 'phonon.template')
        with open(lammps_script, 'w') as f:
            f.write(filltemplate(template, lammps_variables, '<', '>'))
        
        # Run LAMMPS
        lmp.run(lammps_command, script_name=lammps_script, mpi_command=mpi_command)
        
        # Extract forces from dump file
        forcestructure = am.load('atom_dump', 'forces.dump')
        forces = uc.set_in_units(forcestructure.atoms.force, lammps_units['force'])
        forcearrays.append(forces)
    
    results = {}

    # Set computed forces
    phonon.forces = forcearrays
    
    # Save to yaml file    
    phonon.save(f'phonopy_params{istrain}.yaml')
    
    # Compute band structure    
    phonon.produce_force_constants()
    phonon.auto_band_structure(plot=plot)
    results['band_structure'] = phonon.get_band_structure_dict()
    if plot:
        plt.ylabel('Frequency (THz)')
        plt.savefig(Path('.', 'band.png'), dpi=400)
        plt.close()
    
    # Compute density of states
    phonon.auto_total_dos(plot=False)
    phonon.auto_projected_dos(plot=False)
    dos = phonon.get_total_dos_dict()
    dos['frequency'] = uc.set_in_units(dos.pop('frequency_points'), 'THz')
    dos['projected_dos'] = phonon.get_projected_dos_dict()['projected_dos']
    results['dos'] = dos
    
    # Compute thermal properties
    phonon.run_thermal_properties()
    results['thermal_properties'] = phonon.get_thermal_properties_dict()
    phonon.write_yaml_thermal_properties(filename=f"thermal_properties{istrain}.yaml")

    results['phonon'] = phonon
    return results

def save_band_structure(band_structure_dict):
    """Create a JSON file containing the zero strain band structure data"""
    model = DM()
    model['band-structure'] = DM()

    for qpoints in band_structure_dict['qpoints']:
        model['band-structure'].append('qpoints', uc.model(qpoints))

    for distances in band_structure_dict['distances']:
        model['band-structure'].append('distances', uc.model(distances))

    for frequencies in band_structure_dict['frequencies']:
        model['band-structure'].append('frequencies', uc.model(frequencies))
    
    with open(f"band_structure.json", 'w', encoding='UTF-8') as f:
        model.json(fp=f, ensure_ascii=False)
    
def save_density_of_states(dos_dict):
    """Create a JSON file containing the zero strain density of states data"""
    model = DM()
    model['density-of-states'] = DM()
    model['density-of-states']['frequency'] = uc.model(dos_dict['frequency'], 'THz')
    model['density-of-states']['total_dos'] = uc.model(dos_dict['total_dos'])
    model['density-of-states']['projected_dos'] = uc.model(dos_dict['projected_dos'])

    with open(f"density_of_states.json", 'w', encoding='UTF-8') as f:
        model.json(fp=f, ensure_ascii=False)

def save_thermal_properties(thermal_dict):

    data = {}

    # Add zero strain thermal properties
    data['temperature (K)'] = thermal_dict['temperature']
    data['Helmholtz (eV/atom)'] = uc.get_in_units(thermal_dict['Helmholtz'], 'eV')
    data['entropy (J/K/mol)'] = uc.get_in_units(thermal_dict['entropy'], 'J/K/mol')
    data['Cv (J/K/mol)'] = uc.get_in_units(thermal_dict['heat_capacity_v'], 'J/K/mol')

    # Add qha results
    if 'volume' in thermal_dict:
        data['volume (Å^3)'] = uc.get_in_units(thermal_dict['volume'], 'angstrom^3')
        data['thermal expansion'] = thermal_dict['thermal_expansion']
        data['Gibbs (eV/atom)'] = uc.get_in_units(thermal_dict['Gibbs'], 'eV')
        data['bulk modulus (GPa)'] = uc.get_in_units(thermal_dict['bulk_modulus'], 'GPa')
        data['Cp numerical (J/K/mol)'] = uc.get_in_units(thermal_dict['heat_capacity_p_numerical'], 'J/K/mol')
        data['Cp polyfit (J/K/mol)'] = uc.get_in_units(thermal_dict['heat_capacity_p_polyfit'], 'J/K/mol')
        data['gruneisen'] = thermal_dict['gruneisen']

    data = pd.DataFrame(data)

    with open('thermal_properties.csv', 'w', encoding='UTF-8') as f:
        data.to_csv(f, index=False)
