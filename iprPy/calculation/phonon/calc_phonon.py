#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale

# Standard Python libraries
from pathlib import Path
import sys
import uuid
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np

# https://matplotlib.org/
import matplotlib.pyplot as plt

# https://atztogo.github.io/phonopy/phonopy-module.html
import phonopy

# https://atztogo.github.io/spglib/python-spglib.html
import spglib

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calculation metadata
calculation_style = 'phonon'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run phonon
    results_dict = phonon_quasiharmonic(input_dict['lammps_command'],
                          input_dict['ucell'],
                          input_dict['potential'],
                          mpi_command = input_dict['mpi_command'],
                          a_mult = input_dict['sizemults'][0][1] - input_dict['sizemults'][0][0],
                          b_mult = input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0],
                          c_mult = input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0],
                          distance = input_dict['displacementdistance'],
                          symprec = input_dict['symmetryprecision'],
                          strainrange = input_dict['strainrange'],
                          numstrains = input_dict['numstrains'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def phonon_quasiharmonic(lammps_command, ucell, potential, mpi_command=None, a_mult=3, b_mult=3, c_mult=3,
           distance=0.01, symprec=1e-5, strainrange=0.01, numstrains=5):
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
        calculation.  Must be an int and not a tuple.  Default value is 3.
    b_mult : int, optional
        The b size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 3.
    c_mult : int, optional
        The c size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 3.
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
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Get original box vectors
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
        for istrain, strain in zip(istrains, strains):

            # Identify the zero strain run
            if istrain == 0:
                zerostrainrun = True
                savefile = 'phonopy_params.yaml'
            else:
                zerostrainrun = False
                savefile = f'phonopy_params_{istrain}.yaml'
            
            # Generate system at the strain
            newvects = vects * (1 + strain)
            ucell.box_set(vects=newvects, scale=True)
            volumes.append(ucell.box.volume)
            system = ucell.supersize(a_mult, b_mult, c_mult)

            # Define lammps variables
            lammps_variables = {}
            system_info = system.dump('atom_data', f='disp.dat',
                                    potential=potential,
                                    return_pair_info=True)
            lammps_variables['atomman_system_pair_info'] = system_info

            # Set dump_modify_format based on lammps_date
            if lammps_date < datetime.date(2016, 8, 3):
                lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e"'
            else:
                lammps_variables['dump_modify_format'] = 'float %.13e'

            # Write lammps input script
            template_file = 'phonon.template'
            lammps_script = 'phonon.in'
            template = iprPy.tools.read_calc_file(template_file, filedict)
            with open(lammps_script, 'w') as f:
                f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

            # Run LAMMPS
            output = lmp.run(lammps_command, 'phonon.in', mpi_command=mpi_command)

            # Extract system energy
            thermo = output.simulations[0]['thermo']
            energy = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])

            # Scale energy by sizemults and append to list
            energies.append(energy / (a_mult * b_mult * c_mult))

            # Compute phonon info for ucell
            phononinfo = phononcalc(lammps_command, ucell, potential, mpi_command=mpi_command,
                                    a_mult=a_mult, b_mult=b_mult, c_mult=c_mult,
                                    distance=distance, symprec=symprec, savefile=savefile,
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
            free_energy[:, istrain] = phononinfo['thermal_properties']['free_energy']
            entropy[:, istrain] = phononinfo['thermal_properties']['entropy']
            heat_capacity[:, istrain] = phononinfo['thermal_properties']['heat_capacity']
        
        # Compute qha
        try:
            qha = phonopy.PhonopyQHA(volumes=volumes,
                        electronic_energies=energies,
                        temperatures=temperatures,
                        free_energy=free_energy,
                        cv=heat_capacity,
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
        
        results['thermal_properties']['volume'] = uc.set_in_units(np.hstack([qha.get_volume_temperature(), np.nan]), 'angstrom^3')
        results['thermal_properties']['thermal_expansion'] = np.hstack([qha.get_thermal_expansion(), np.nan])
        results['thermal_properties']['Gibbs'] = uc.set_in_units(np.hstack([qha.get_gibbs_temperature(), np.nan]), 'eV')
        results['thermal_properties']['bulk_modulus'] = uc.set_in_units(np.hstack([qha.get_bulk_modulus_temperature(), np.nan]), 'GPa')
        results['thermal_properties']['heat_capacity_p_numerical'] = uc.set_in_units(np.hstack([qha.get_heat_capacity_P_numerical(), np.nan]), 'J/K/mol')
        results['thermal_properties']['heat_capacity_p_polyfit'] = uc.set_in_units(np.hstack([qha.get_heat_capacity_P_polyfit(), np.nan]), 'J/K/mol')
        results['thermal_properties']['gruneisen'] = np.hstack([qha.get_gruneisen_temperature(), np.nan])
    
    return results


def phononcalc(lammps_command, ucell, potential, mpi_command=None,
               a_mult=3, b_mult=3, c_mult=3, distance=0.01, symprec=1e-5, 
               savefile='phonopy_params.yaml', plot=True, lammps_date=None):
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
        calculation.  Must be an int and not a tuple.  Default value is 3.
    b_mult : int, optional
        The b size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 3.
    c_mult : int, optional
        The c size multiplier to use on ucell before running the phonon
        calculation.  Must be an int and not a tuple.  Default value is 3.
    distance : float, optional
        The atomic displacement distance used for computing the phonons.
        Default value is 0.01.
    symprec : float, optional
        Absolute length tolerance to use in identifying symmetry of atomic
        sites and system boundaries. Default value is 1e-5.
    savefile: str, optional
        The name of the phonopy yaml backup file.  Default value is
        'phonopy_params.yaml'.
    plot : bool, optional
        Flag indicating if band structure and DOS figures are to be generated.
        Default value is True.
    lammps_date : datetime.date, optional
        The version date associated with lammps_command.  If not given, the
        version will be identified.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    if lammps_date is None:
        lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Use spglib to find primitive unit cell of ucell
    convcell = ucell.dump('spglib_cell')
    primcell = spglib.find_primitive(convcell, symprec=symprec)
    primucell = am.load('spglib_cell', primcell, symbols=ucell.symbols).normalize()
    
    # Initialize Phonopy object
    phonon = phonopy.Phonopy(primucell.dump('phonopy_Atoms', symbols=potential.elements(primucell.symbols)),
                             [[a_mult, 0, 0], [0, b_mult, 0], [0, 0, c_mult]],
                             factor=phonopy.units.VaspToTHz)
    phonon.generate_displacements(distance=distance)
    
    # Loop over displaced supercells to compute forces
    forcearrays = []
    for supercell in phonon.supercells_with_displacements:
        
        # Save to LAMMPS data file
        system = am.load('phonopy_Atoms', supercell, symbols=primucell.symbols)
        system_info = system.dump('atom_data', f='disp.dat',
                                  potential=potential,
                                  return_pair_info=True)
        
        # Define lammps variables
        lammps_variables = {}
        lammps_variables['atomman_system_pair_info'] = system_info

        # Set dump_modify_format based on lammps_date
        if lammps_date < datetime.date(2016, 8, 3):
            lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e"'
        else:
            lammps_variables['dump_modify_format'] = 'float %.13e'

        # Write lammps input script
        template_file = 'phonon.template'
        lammps_script = 'phonon.in'
        template = iprPy.tools.read_calc_file(template_file, filedict)
        with open(lammps_script, 'w') as f:
            f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
        
        # Run LAMMPS
        lmp.run(lammps_command, 'phonon.in', mpi_command=mpi_command)
        
        # Extract forces from dump file
        forcestructure = am.load('atom_dump', 'forces.dump')
        forces = uc.set_in_units(forcestructure.atoms.force, lammps_units['force'])
        forcearrays.append(forces)
    
    results = {}

    # Set computed forces
    phonon.set_forces(forcearrays)
    
    # Save to yaml file    
    phonon.save(savefile)
    
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
    
    results['phonon'] = phonon
    return results

def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    # Set script's name
    input_dict['script'] = script
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['numstrains'] = int(input_dict.get('numstrains', 5))
    
    # These are calculation-specific default unitless floats
    input_dict['symmetryprecision'] = float(input_dict.get('symmetryprecision', 1e-5))
    input_dict['strainrange'] = float(input_dict.get('strainrange', 0.01))
    
    # These are calculation-specific default floats with units
    input_dict['displacementdistance'] = iprPy.input.value(input_dict, 'displacementdistance',
                                                default_unit=input_dict['length_unit'],
                                                default_term='0.01 angstrom')

    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)

    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)
        
if __name__ == '__main__':
    main(*sys.argv[1:])