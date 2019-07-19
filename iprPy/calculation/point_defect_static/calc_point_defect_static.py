#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
import sys
import uuid
import shutil
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define record_style
record_style = 'calculation_point_defect_static'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run ptd_energy to refine values
    results_dict = calc(input_dict['lammps_command'],
                        input_dict['initialsystem'],
                        input_dict['potential'],
                        input_dict['point_kwargs'],
                        1.05 * input_dict['ucell'].box.a,
                        mpi_command = input_dict['mpi_command'],
                        etol = input_dict['energytolerance'],
                        ftol = input_dict['forcetolerance'],
                        maxiter = input_dict['maxiterations'],
                        maxeval = input_dict['maxevaluations'],
                        dmax = input_dict['maxatommotion'])
    
    # Save data model of results
    script = Path(__file__).stem
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def calc(lammps_command, system, potential, point_kwargs, cutoff,
         mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000,
         maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
         tol=uc.set_in_units(1e-5, 'angstrom')):
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy. Evaluates a relaxed system containing a point defect
    to determine if the defect structure has transformed to a different
    configuration.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float
        Cutoff distance to use in identifying neighbor atoms.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simuation in.  If not
        given, will use the current working directory.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    tol : float, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_coh'** (*float*) - The cohesive energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point.defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
        relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
        relaxed defect system.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
        for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
        for the relaxed defect system.
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
        has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.array of float*) - The centrosummation
        parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.array of float*) - The position_shift
        parameter used for evaluating if the configuration has relaxed.
        Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.array of float*) - The db_vect_shift
        parameter used for evaluating if the configuration has relaxed.
        Only given for dumbbell-style defects.
    """
    
    # Run ptd_energy to refine values
    results_dict = pointdefect(lammps_command,
                               system,
                               potential,
                               point_kwargs,
                               mpi_command = mpi_command,
                               etol = etol,
                               ftol = ftol,
                               maxiter = maxiter,
                               maxeval = maxeval,
                               dmax = dmax)
    
    # Run check_ptd_config
    results_dict2 = check_ptd_config(results_dict['system_ptd'],
                                     point_kwargs,
                                     cutoff)
    results_dict.update(results_dict2)

    return results_dict

def pointdefect(lammps_command, system, potential, point_kwargs,
                mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000,
                maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Adds one or more point defects to a system and evaluates the defect 
    formation energy.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sim_directory : str, optional
        The path to the directory to perform the simuation in.  If not
        given, will use the current working directory.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'E_coh'** (*float*) - The cohesive energy of the bulk system.
        - **'E_ptd_f'** (*float*) - The point.defect formation energy.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_ptd'** (*float*) - The total potential energy of the
          relaxed defect system.
        - **'system_base'** (*atomman.System*) - The relaxed bulk system.
        - **'system_ptd'** (*atomman.System*) - The relaxed defect system.
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed bulk system.
        - **'dumpfile_ptd'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed defect system.
    """
    # Get script's location
    script_dir = Path(__file__).parent

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='perfect.dat',
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    
    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = Path(script_dir, 'min.template')
    lammps_script = 'min.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    # Run lammps to relax perfect.dat
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract LAMMPS thermo data.
    thermo = output.simulations[0]['thermo']
    E_total_base = uc.set_in_units(thermo.PotEng.values[-1],
                                   lammps_units['energy'])
    E_coh = E_total_base / system.natoms
    
    pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
    pressure_base = np.array([[pxx, pxy, pxz], [pxy, pyy, pyz], [pxz, pyz, pzz]])
    
    # Rename log file
    shutil.move('log.lammps', 'min-perfect-log.lammps')
    
    # Load relaxed system from dump file and copy old box vectors because 
    # dump files crop the values.
    last_dump_file = 'atom.' + str(thermo.Step.values[-1])
    system_base = am.load('atom_dump', last_dump_file, symbols=system.symbols)
    system_base.box_set(vects=system.box.vects)
    system_base.dump('atom_dump', f='perfect.dump')
    
    # Add defect(s)
    system_ptd = deepcopy(system_base)
    if not isinstance(point_kwargs, (list, tuple)):
        point_kwargs = [point_kwargs]
    for pkwargs in point_kwargs:
        system_ptd = am.defect.point(system_ptd, **pkwargs)
    
    # Update lammps variables
    system_info = system_ptd.dump('atom_data', f='defect.dat',
                                  units = potential.units, 
                                  atom_style = potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    
    # Write lammps input script
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run lammps
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract lammps thermo data
    thermo = output.simulations[0]['thermo']
    E_total_ptd = uc.set_in_units(thermo.PotEng.values[-1],
                                  lammps_units['energy'])
    pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
    pressure_ptd = np.array([[pxx, pxy, pxz], [pxy, pyy, pyz], [pxz, pyz, pzz]])
    
    # Rename log file
    shutil.move('log.lammps', 'min-defect-log.lammps')
    
    # Load relaxed system from dump file and copy old vects as 
    # the dump files crop the values
    last_dump_file = 'atom.'+str(thermo.Step.values[-1])
    system_ptd = am.load('atom_dump', last_dump_file, symbols=system_ptd.symbols)
    system_ptd.box_set(vects=system.box.vects)
    system_ptd.dump('atom_dump', f='defect.dump')
    
    # Compute defect formation energy
    E_ptd_f = E_total_ptd - E_coh * system_ptd.natoms
    
    # Compute strain tensor
    pij = -(pressure_base - pressure_ptd) * system_base.box.volume
    
    # Cleanup files
    for fname in script_dir.glob('atom.*'):
        fname.unlink()
    for dumpjsonfile in script_dir.glob('*.dump.json'):
        dumpjsonfile.unlink()
    
    # Return results
    results_dict = {}
    results_dict['E_coh'] = E_coh
    results_dict['E_ptd_f'] = E_ptd_f
    results_dict['E_total_base'] = E_total_base
    results_dict['E_total_ptd'] = E_total_ptd
    results_dict['pij_tensor'] = pij
    results_dict['system_base'] = system_base
    results_dict['system_ptd'] = system_ptd
    results_dict['dumpfile_base'] = 'perfect.dump'
    results_dict['dumpfile_ptd'] = 'defect.dump'
    
    return results_dict

def check_ptd_config(system, point_kwargs, cutoff,
                     tol=uc.set_in_units(1e-5, 'angstrom')):
    """
    Evaluates a relaxed system containing a point defect to determine if the
    defect structure has transformed to a different configuration.
    
    Parameters
    ----------
    system : atomman.System
        The relaxed defect system.
    point_kwargs : dict or list of dict
        One or more dictionaries containing the keyword arguments for
        the atomman.defect.point() function to generate specific point
        defect configuration(s).
    cutoff : float
        Cutoff distance to use in identifying neighbor atoms.
    tol : float, optional
        Absolute tolerance to use for identifying if a defect has
        reconfigured (default is 1e-5 Angstoms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'has_reconfigured'** (*bool*) - Flag indicating if the structure
          has been identified as relaxing to a different defect configuration.
        - **'centrosummation'** (*numpy.array of float*) - The centrosummation
          parameter used for evaluating if the configuration has relaxed.
        - **'position_shift'** (*numpy.array of float*) - The position_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for interstitial and substitutional-style defects.
        - **'db_vect_shift'** (*numpy.array of float*) - The db_vect_shift
          parameter used for evaluating if the configuration has relaxed.
          Only given for dumbbell-style defects.
    """
    
    # Check if point_kwargs is a list
    if not isinstance(point_kwargs, (list, tuple)):
        pos = point_kwargs['pos']
    
    # If it is a list of 1, use that set
    elif len(point_kwargs) == 1:
        point_kwargs = point_kwargs[0]
        pos = point_kwargs['pos']
        
    # If it is a list of two (divacancy), use the first and average position
    elif len(point_kwargs) == 2:
        pos = (np.array(point_kwargs[0]['pos'])
               + np.array(point_kwargs[1]['pos'])) / 2
        point_kwargs = point_kwargs[0]
    
    # More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')

    # Initially set has_reconfigured to False
    has_reconfigured = False
    
    # Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.pos, pos) 
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    
    # Calculate centrosummation by summing up the positions of the close atoms
    centrosummation = np.sum(pos_vects[pos_mags < cutoff], axis=0)
    
    if not np.allclose(centrosummation, np.zeros(3), atol=tol):
        has_reconfigured = True
        
    # Calculate shift of defect atom's position if interstitial or substitutional
    if point_kwargs['ptd_type'] == 'i' or point_kwargs['ptd_type'] == 's':
        position_shift = system.dvect(system.natoms-1, pos)
       
        if not np.allclose(position_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation,
                'position_shift': position_shift}
        
    # Investigate if dumbbell vector has shifted direction 
    elif point_kwargs['ptd_type'] == 'db':
        db_vect = point_kwargs['db_vect'] / np.linalg.norm(point_kwargs['db_vect'])
        new_db_vect = system.dvect(-2, -1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation,
                'db_vect_shift': db_vect_shift}
    
    else:
        return {'has_reconfigured': has_reconfigured,
                'centrosummation': centrosummation}

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
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '5 5 5')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.subset('lammps_minimize').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)
    
    # Load point defect parameters
    iprPy.input.subset('pointdefect').interpret(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])