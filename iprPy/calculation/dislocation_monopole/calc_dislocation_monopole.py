#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys
import uuid
import glob
import shutil
import random
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
record_style = 'calculation_dislocation_monopole'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
   
    results_dict = dislocationmonopole(input_dict['lammps_command'],
                                       input_dict['initialsystem'],
                                       input_dict['potential'],
                                       input_dict['burgersvector'],
                                       input_dict['C'],
                                       mpi_command = input_dict['mpi_command'],
                                       axes = input_dict['transformationmatrix'],
                                       m = input_dict['stroh_m'],
                                       n = input_dict['stroh_n'],
                                       lineboxvector  = input_dict['dislocation_lineboxvector'],
                                       etol = input_dict['energytolerance'],
                                       ftol = input_dict['forcetolerance'],
                                       maxiter = input_dict['maxiterations'],
                                       maxeval = input_dict['maxevaluations'],
                                       dmax = input_dict['maxatommotion'],
                                       annealtemp =  input_dict['annealtemperature'],
                                       randomseed = input_dict['randomseed'],
                                       bshape = input_dict['dislocation_boundaryshape'],
                                       bwidth = input_dict['boundarywidth'])
    
    # Save data model of results
    script = os.path.splitext(os.path.basename(__file__))[0]
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def dislocationmonopole(lammps_command, system, potential, burgers,
                        C, mpi_command=None, axes=None, m=[0,1,0], n=[0,0,1],
                        lineboxvector='a', randomseed=None,
                        etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
                        dmax=uc.set_in_units(0.01, 'angstrom'),
                        annealtemp=0.0, bshape='circle',
                        bwidth=uc.set_in_units(10, 'angstrom')):
    """
    Creates and relaxes a dislocation monopole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The bulk system to add the defect to.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    burgers : list or numpy.array of float
        The burgers vector for the dislocation being added.
    C : atomman.ElasticConstants
        The system's elastic constants.
    mpi_command : str or None, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    axes : numpy.array of float or None, optional
        The 3x3 axes used to rotate the system by during creation.  If given,
        will be used to transform burgers and C from the standard
        crystallographic orientations to the system's Cartesian units.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
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
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. (Default is 0.0,
        which will skip the dynamic relaxation.)
    bshape : str, optional
        The shape to make the boundary region.  Options are 'circle' and
        'rect' (default is 'circle').
    bwidth : float, optional
        The minimum thickness of the boundary region (default is 10
        Angstroms).
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed base system.
        - **'symbols_base'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the base system's
          atypes.
        - **'Stroh_preln'** (*float*) - The pre-logarithmic factor in the 
          dislocation's self-energy expression.
        - **'Stroh_K_tensor'** (*numpy.array of float*) - The energy
          coefficient tensor based on the dislocation's Stroh solution.
        - **'dumpfile_disl'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed dislocation monopole system.
        - **'symbols_disl'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the dislocation
          monopole system's atypes.
        - **'E_total_disl'** (*float*) - The total potential energy of the
          dislocation monopole system.
    """
    # Initialize results dict
    results_dict = {}
    
    # Save initial perfect system
    system.dump('atom_dump', f='base.dump')
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = system.symbols
    
    # Solve Stroh method for dislocation
    stroh = am.defect.Stroh(C, burgers, axes=axes, m=m, n=n)
    results_dict['Stroh_preln'] = stroh.preln
    results_dict['Stroh_K_tensor'] = stroh.K_tensor
    
    # Generate dislocation system by displacing atoms
    disp = stroh.displacement(system.atoms.pos)
    system.atoms.pos += disp
    
    # Apply fixed boundary conditions
    system = disl_boundary_fix(system, bwidth, bshape=bshape, lineboxvector=lineboxvector, m=m, n=n)
    
    # Relax system
    relaxed = disl_relax(lammps_command, system, potential,
                         mpi_command = mpi_command, 
                         annealtemp = annealtemp,
                         etol = etol, 
                         ftol = ftol, 
                         maxiter = maxiter, 
                         maxeval = maxeval)
    
    # Save relaxed dislocation system with original box vects
    system_disl = am.load('atom_dump', relaxed['dumpfile'], symbols=system.symbols)
    
    system_disl.box_set(vects=system.box.vects, origin=system.box.origin)
    system_disl.dump('atom_dump', f='disl.dump')
    results_dict['dumpfile_disl'] = 'disl.dump'
    results_dict['symbols_disl'] = system_disl.symbols
    
    results_dict['E_total_disl'] = relaxed['E_total']
    
    # Cleanup files
    os.remove('0.dump')
    os.remove(relaxed['dumpfile'])
    for dumpjsonfile in glob.iglob('*.dump.json'):
        os.remove(dumpjsonfile)
    
    return results_dict

def disl_boundary_fix(system, bwidth, bshape='circle', lineboxvector='a', m=None, n=None):
    """
    Creates a boundary region by changing atom types.
    
    Parameters
    ----------
    system : atomman.System
        The system to add the boundary region to.
    bwidth : float
        The minimum thickness of the boundary region.
    bshape : str, optional
        The shape to make the boundary region.  Options are 'circle' and
        'box' (default is 'circle').
    lineboxvector : str, optional
        Specifies which of the three box vectors (a, b, or c) the dislocation line is to be
        parallel to.  Default value is 'a'.
    m : array-like object, optional
        Cartesian vector used by the Stroh solution, which is perpendicular to both
        lineboxvector and n.  Default value is [0, 1, 0], which assumes the default value
        for the lineboxvector.
    n : array-like object, optional
        Cartesian vector used by the Stroh solution, which is perpendicular to both
        lineboxvector and m.  Default value is [0, 0, 1], which assumes the default value
        for the lineboxvector.
        
    """
    # Set default values
    if m is None:
        m = np.array([0, 1, 0])
    m = np.asarray(m)
    if n is None:
        n = np.array([0, 0, 1])
    n = np.asarray(n)
    
    # Extract values from system
    natypes = system.natypes
    atype = system.atoms_prop(key='atype')
    pos = system.atoms.pos
    
    # Set line_box_velineboxvectorctor dependent values
    if lineboxvector == 'a':
        u = system.box.avect / system.box.a
        boxvect1 = system.box.bvect
        boxvect2 = system.box.cvect
        pbc = (True, False, False)

    elif lineboxvector == 'b':
        u = system.box.bvect / system.box.b
        boxvect1 = system.box.cvect
        boxvect2 = system.box.avect
        pbc = (False, True, False)

    elif lineboxvector == 'c':
        u = system.box.cvect / system.box.c
        boxvect1 = system.box.avect
        pbc = (False, False, True)

    # Assert u, m, n are all orthogonal
    assert np.isclose(np.dot(u, m), 0.0)
    assert np.isclose(np.dot(u, n), 0.0)
    assert np.isclose(np.dot(m, n), 0.0)
    
    # Get components within mn plane
    mn = np.array([m, n])
    mnvect1 = mn.dot(boxvect1)
    mnvect2 = mn.dot(boxvect2)
    mnorigin = mn.dot(system.box.origin)
    mnpos = mn.dot(pos.T).T
    
    # Compute normal vectors to box vectors
    normal_mnvect1 = np.array([-mnvect1[1], mnvect1[0]])
    normal_mnvect2 = np.array([mnvect2[1], -mnvect2[0]])
    normal_mnvect1 = normal_mnvect1 / np.linalg.norm(normal_mnvect1)
    normal_mnvect2 = normal_mnvect2 / np.linalg.norm(normal_mnvect2)
    
    # Find two opposite boundary corners 
    botcorner = mnorigin
    topcorner = mnorigin + mnvect1 + mnvect2
    
    if bshape == 'box':
        # Project all positions normal to the two mnvectors
        pos_normal_1 = np.dot(mnpos, normal_mnvect1)
        pos_normal_2 = np.dot(mnpos, normal_mnvect2)

        # Adjust atypes of boundary atoms
        atype[(pos_normal_1 < np.dot(botcorner, normal_mnvect1) + bwidth)
             |(pos_normal_2 < np.dot(botcorner, normal_mnvect2) + bwidth)
             |(pos_normal_1 > np.dot(topcorner, normal_mnvect1) - bwidth)
             |(pos_normal_2 > np.dot(topcorner, normal_mnvect2) - bwidth)] += natypes
    
    elif bshape == 'circle':
        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0]*p2[1] - p2[0]*p1[1])
            return A, B, -C

        def intersection(L1, L2):
            D  = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return False

        # Find two opposite boundary corners 
        botcorner = mnorigin
        topcorner = mnorigin + mnvect1 + mnvect2

        # Define normal lines
        normal_line_1 = line([0,0], normal_mnvect1)
        normal_line_2 = line([0,0], normal_mnvect2)

        # Define boundary lines
        bound_bot1 = line(botcorner, botcorner+mnvect1)
        bound_bot2 = line(botcorner, botcorner+mnvect2)
        bound_top1 = line(topcorner, topcorner+mnvect1)
        bound_top2 = line(topcorner, topcorner+mnvect2)

        # Identify intersection points
        intersections = np.array([intersection(normal_line_1, bound_bot1),
                                  intersection(normal_line_2, bound_bot2),
                                  intersection(normal_line_1, bound_top1),
                                  intersection(normal_line_2, bound_top2)])

        # Compute cylinder radius
        radius = np.min(np.linalg.norm(intersections, axis=1)) - bwidth

        # Adjust atypes of boundary atoms
        atype[np.linalg.norm(mnpos, axis=1) > radius] += natypes
    
    else:
        raise ValueError("Unknown boundary shape type! Enter 'circle' or 'box'")
    
    newsystem = deepcopy(system)
    newsystem.atoms.atype = atype
    newsystem.symbols = list(system.symbols) * 2
    newsystem.pbc = pbc
    newsystem.wrap()

    return newsystem

def disl_relax(lammps_command, system, potential,
               mpi_command=None, annealtemp=0.0, randomseed=None,
               etol=0.0, ftol=1e-6, maxiter=10000, maxeval=100000,
               dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Sets up and runs the disl_relax.in LAMMPS script for relaxing a
    dislocation monopole system.
    
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
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. (Default is 0.0,
        which will skip the dynamic relaxation.)
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
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
        
        - **'logfile'** (*str*) - The name of the LAMMPS log file.
        - **'dumpfile'** (*str*) - The name of the LAMMPS dump file
          for the relaxed system.
        - **'E_total'** (*float*) - The total potential energy for the
          relaxed system.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='system.dat',
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
    lammps_variables['anneal_info'] = anneal_info(annealtemp, randomseed,
                                                  potential.units)
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    lammps_variables['group_move'] = ' '.join(np.array(range(1, system.natypes // 2 + 1), dtype=str))
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = 'disl_relax.template'
    lammps_script = 'disl_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    thermo = output.simulations[-1]['thermo']
    
    # Extract output values
    results = {}
    results['logfile'] = 'log.lammps'
    results['dumpfile'] = '%i.dump' % thermo.Step.values[-1] 
    results['E_total'] = uc.set_in_units(thermo.PotEng.values[-1],
                                         lammps_units['energy'])
    
    return results

def anneal_info(temperature=0.0, randomseed=None, units='metal'):
    """
    Generates LAMMPS commands for thermo anneal.
    
    Parameters
    ----------
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    units : str, optional
        The LAMMPS units style to use (default is 'metal').
    
    Returns
    -------
    str
        The generated LAMMPS input lines for performing a dynamic relax.
        Will be '' if temperature==0.0.
    """    
    # Return nothing if temperature is 0.0 (don't do thermo anneal)
    if temperature == 0.0:
        return ''
    
    # Generate velocity, fix nvt, and run LAMMPS command lines
    else:
        if randomseed is None:
            randomseed = random.randint(1, 900000000)
        
        start_temp = 2 * temperature
        tdamp = 100 * lmp.style.timestep(units)
        timestep = lmp.style.timestep(units)
        info = '\n'.join([
            'velocity move create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
            'fix nvt all nvt temp %f %f %f' % (temperature, temperature,
                                               tdamp),
            'timestep %f' % (timestep),
            'thermo 10000',
            'run 10000',
            ])
    
    return info

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
    iprPy.input.interpret('units', input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '0 3 -20 20 -20 20')
    input_dict['dislocation_boundaryshape'] = input_dict.get('dislocation_boundaryshape',
                                                             'circle')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['randomseed'] =     int(input_dict.get('randomseed',
                                       random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['annealtemperature'] = float(input_dict.get('annealtemperature',
                                                           0.0))
    input_dict['dislocation_boundarywidth'] = float(input_dict.get('dislocation_boundarywidth', 3.0))
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.interpret('lammps_commands', input_dict)
    
    # Set default system minimization parameters
    iprPy.input.interpret('lammps_minimize', input_dict)
    
    # Load potential
    iprPy.input.interpret('lammps_potential', input_dict)
    
    # Load ucell system
    iprPy.input.interpret('atomman_systemload', input_dict, build=build)
    
    # Load dislocation parameters
    iprPy.input.interpret('dislocationmonopole', input_dict)
    
    # Multiply boundarywidth by alat
    if input_dict['ucell'] is not None:
        input_dict['boundarywidth'] = input_dict['ucell'].box.a * input_dict['dislocation_boundarywidth']

    # Load elastic constants
    iprPy.input.interpret('atomman_elasticconstants', input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.interpret('atomman_systemmanipulate', input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])