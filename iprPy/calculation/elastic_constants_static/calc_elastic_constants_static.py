#!/usr/bin/env python
# coding: utf-8

# Python script created by Lucas Hale
# Built around LAMMPS script by Steve Plimpton

# Standard library imports
from pathlib import Path
import sys
import uuid

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

# Define calculation metadata
calculation_style = 'elastic_constants_static'
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
    
    # Run lammps_ELASTIC_refine to refine values
    results_dict = elastic_constants_static(input_dict['lammps_command'],
                                            input_dict['initialsystem'],
                                            input_dict['potential'],
                                            mpi_command = input_dict['mpi_command'],
                                            strainrange = input_dict['strainrange'],
                                            etol = input_dict['energytolerance'],
                                            ftol = input_dict['forcetolerance'],
                                            maxiter = input_dict['maxiterations'],
                                            maxeval = input_dict['maxevaluations'],
                                            dmax = input_dict['maxatommotion'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def elastic_constants_static(lammps_command, system, potential, mpi_command=None,
                             strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=10000,
                             maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Repeatedly runs the ELASTIC example distributed with LAMMPS until box
    dimensions converge within a tolerance.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    strainrange : float, optional
        The small strain value to apply when calculating the elastic
        constants (default is 1e-6).
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 10000).
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
        
        - **'a_lat'** (*float*) - The relaxed a lattice constant.
        - **'b_lat'** (*float*) - The relaxed b lattice constant.
        - **'c_lat'** (*float*) - The relaxed c lattice constant.
        - **'alpha_lat'** (*float*) - The alpha lattice angle.
        - **'beta_lat'** (*float*) - The beta lattice angle.
        - **'gamma_lat'** (*float*) - The gamma lattice angle.
        - **'E_coh'** (*float*) - The cohesive energy of the relaxed system.
        - **'stress'** (*numpy.array*) - The measured stress state of the
          relaxed system.
        - **'C_elastic'** (*atomman.ElasticConstants*) - The relaxed system's
          elastic constants.
        - **'system_relaxed'** (*atomman.System*) - The relaxed system.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}

    # Convert hexagonal cells to orthorhombic to avoid LAMMPS tilt issues
    if am.tools.ishexagonal(system.box):
        system = system.rotate([[2,-1,-1,0], [0, 1, -1, 0], [0,0,0,1]])
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='init.dat',
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
    lammps_variables['strainrange'] = strainrange
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Fill in template files
    template_file = 'cij.template'
    lammps_script = 'cij.in'
    template = iprPy.tools.read_calc_file(template_file, filedict)
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    template_file2 = 'potential.template'
    lammps_script2 = 'potential.in'
    template = iprPy.tools.read_calc_file(template_file2, filedict)
    with open(lammps_script2, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Pull out initial state
    thermo = output.simulations[0]['thermo']
    pxx0 = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
    pyy0 = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
    pzz0 = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
    pyz0 = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
    pxz0 = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
    pxy0 = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
    
    # Negative strains
    cij_n = np.empty((6,6))
    for i in range(6):
        j = 1 + i * 2
        # Pull out strained state
        thermo = output.simulations[j]['thermo']
        pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
        pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
        pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
        pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
        pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
        pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
        
        # Calculate cij_n using stress changes
        cij_n[i] = np.array([pxx - pxx0, pyy - pyy0, pzz - pzz0,
                             pyz - pyz0, pxz - pxz0, pxy - pxy0]) / strainrange
    
    # Positive strains
    cij_p = np.empty((6,6))
    for i in range(6):
        j = 2 + i * 2
        # Pull out strained state
        thermo = output.simulations[j]['thermo']
        pxx = uc.set_in_units(thermo.Pxx.values[-1], lammps_units['pressure'])
        pyy = uc.set_in_units(thermo.Pyy.values[-1], lammps_units['pressure'])
        pzz = uc.set_in_units(thermo.Pzz.values[-1], lammps_units['pressure'])
        pyz = uc.set_in_units(thermo.Pyz.values[-1], lammps_units['pressure'])
        pxz = uc.set_in_units(thermo.Pxz.values[-1], lammps_units['pressure'])
        pxy = uc.set_in_units(thermo.Pxy.values[-1], lammps_units['pressure'])
        
        # Calculate cij_p using stress changes
        cij_p[i] = np.array([pxx - pxx0, pyy - pyy0, pzz - pzz0,
                              pyz - pyz0, pxz - pxz0, pxy - pxy0]) / -strainrange
    
    # Average symmetric values
    cij = (cij_n + cij_p) / 2
    for i in range(6):
        for j in range(i):
            cij[i,j] = cij[j,i] = (cij[i,j] + cij[j,i]) / 2
    
    # Define results_dict
    results_dict = {}
    results_dict['raw_cij_negative'] = cij_n
    results_dict['raw_cij_positive'] = cij_p
    results_dict['C'] = am.ElasticConstants(Cij=cij)
    
    return results_dict

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
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
                                                  
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    input_dict['strainrange'] = float(input_dict.get('strainrange', 1e-6))
    
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
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])