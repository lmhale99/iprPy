#!/usr/bin/env python2.7

# Standard library imports
import os
import subprocess
from multiprocessing import Pool
from copy import deepcopy
import sys
import tempfile
import json
from collections import OrderedDict
import uuid
from math import ceil
from scipy.interpolate import griddata

#Additional imports
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.collections import PatchCollection

#Custom imports
import atomman as am
from atomman.tools import mag, nye, dd
from atomman.tools.stroh import *
from atomman.tools.plot_tools import *

def disl_relax_script(system_info, pair_info, moving_atypes, temp = 0):
    #Perform energy minimization (and possibly NVT) on dislocation monopole system in file read_data
    
    group_move = ''
    for atype in moving_atypes:
        group_move += ' '+str(atype)

    newline = '\n'
    script = newline.join([system_info,
                           '',
                           pair_info,
                           '',
                           'group move type' + group_move,
                           'group hold subtract all move',
                           '',
                           'compute peatom all pe/atom',
                           '',
                           'dump first all custom 100000 atom.* id type x y z c_peatom',
                           'dump_modify first format "%d %d %.13e %.13e %.13e %.13e"',
                           'thermo_style custom step pe',
                           ''])
    if temp == 0.0:
        script = newline.join([script, 
                               'fix nomove hold setforce 0.0 0.0 0.0',
                               'minimize 0 1e-5 10000 100000'])
    else:
        script = newline.join([script,
                               'velocity move create %f 9467 mom yes rot yes dist gaussian'%(2 * temp),
                               'fix nomove hold setforce 0.0 0.0 0.0',
                               'timestep 0.001',
                               'thermo 10000',
                               'fix 1 all nvt temp %f %f 0.1'%(temp, temp),
                               '',
                               'run 10000',
                               'minimize 0 1e-5 10000 100000'])  
    return script

def boundaryfix(system, b_width, shape):
    #Modify the box size and atom types to support the boundary conditions for disl_relax_script
    
    natypes = system.natypes()
    
    if shape == 'circle':
        #find x or y bound closest to 0
        smallest_xy = min([abs(system.box('xlo')), 
                           abs(system.box('xhi')),
                           abs(system.box('ylo')),
                           abs(system.box('yhi'))])
        
        radius = smallest_xy - b_width
        for i in xrange(system.natoms()):
            if mag(system.atoms(i,'pos')[:2]) > radius:
                system.atoms(i, 'atype', system.atoms(i, 'atype') + natypes)
    
    elif shape == 'rect':
        for i in xrange(system.natoms()):
            if (system.atoms(i, 'pos', 0) < system.box('xlo') + b_width or 
                system.atoms(i, 'pos', 0) > system.box('xhi') - b_width or 
                system.atoms(i, 'pos', 1) < system.box('ylo') + b_width or 
                system.atoms(i, 'pos', 1) > system.box('yhi') - b_width):
           
                system.atoms(i, 'atype', system.atoms(i, 'atype') + natypes)
           
    else:
        raise ValueError("Unknown shape type! Enter 'circle' or 'rect'")

def read_input(fname):    
    with open(fname) as f:
        input_dict = {}
        for line in f:
            terms = line.split()
            if len(terms) == 0 or terms[0][0] == '#':
                pass
            elif len(terms) == 2:
                if terms[0] == 'number_of_processors':
                    input_dict['np'] = int(terms[1])
                elif terms[0] == 'lammps_exe':
                    input_dict['lammps_exe'] = terms[1]
                elif terms[0] == 'potential_file':
                    input_dict['potential_file'] = terms[1]
                elif terms[0] == 'potential_dir':
                    input_dict['potential_dir'] = terms[1]
                elif terms[0] == 'prototype_file':
                    input_dict['prototype_file'] = terms[1]
                elif terms[0] == 'phase_file':
                    input_dict['phase_file'] = terms[1]
                elif terms[0] == 'dislocation_file':
                    input_dict['dislocation_file'] = terms[1]
                elif terms[0] == 'dislocation_type':
                    input_dict['dislocation_type'] = terms[1]                    
                elif terms[0] == 'system_size_x':
                    input_dict['system_size_x'] = int(terms[1])
                elif terms[0] == 'system_size_y':
                    input_dict['system_size_y'] = int(terms[1])
                elif terms[0] == 'system_size_z':
                    input_dict['system_size_z'] = int(terms[1]) 
                elif terms[0] == 'boundary_width':
                    input_dict['boundary_width'] = float(terms[1])
                elif terms[0] == 'boundary_shape':
                    assert terms[1] == 'circle' or terms[1] == 'rectangle', 'Invalid boundary shape'
                    input_dict['boundary_shape'] = terms[1]
                elif terms[0] == 'plot_range_x_min':
                    input_dict['plot_range_x_min'] = float(terms[1])
                elif terms[0] == 'plot_range_x_max':
                    input_dict['plot_range_x_max'] = float(terms[1])
                elif terms[0] == 'plot_range_y_min':
                    input_dict['plot_range_y_min'] = float(terms[1])
                elif terms[0] == 'plot_range_y_max':
                    input_dict['plot_range_y_max'] = float(terms[1])                    
                elif terms[0] == 'dd_scale':
                    input_dict['dd_scale'] = float(terms[1])
                elif terms[0] == 'anneal_temperature':
                    input_dict['anneal_temperature'] = float(terms[1])
                else:
                    raise ValueError('Invalid input file')
            else: 
                raise ValueError('Invalid input file')
    
    #test for values (and set defaults if needed)
    try:
        test = input_dict['np']
    except:
        input_dict['np'] = 1
    try:
        test = input_dict['lammps_exe']
    except:
        raise ValueError('lammps_exe not supplied')
    try:
        test = input_dict['potential_file']
    except:
        raise ValueError('potential_file not supplied')
    try:
        test = input_dict['potential_dir']
    except:
        input_dict['potential_dir'] = os.getcwd()
    try:
        test = input_dict['prototype_file']
    except:
        raise ValueError('prototype_file not supplied')
    try:
        test = input_dict['phase_file']
    except:
        raise ValueError('phase_file not supplied')
    try:
        test = input_dict['dislocation_file']
    except:
        raise ValueError('dislocation_file not supplied')
    try:
        test = input_dict['dislocation_type']
    except:
        raise ValueError('dislocation_type not supplied')
    try:
        test = input_dict['system_size_x']
    except:
        input_dict['system_size_x'] = 40
    try:
        test = input_dict['system_size_y']
    except:
        input_dict['system_size_y'] = 40
    try:
        test = input_dict['system_size_z']
    except:
        input_dict['system_size_z'] = 1
    try:
        test = input_dict['boundary_width']
    except:
        input_dict['boundary_width'] = 3.0
    try:
        test = input_dict['boundary_shape']
    except:
        input_dict['boundary_shape'] = 'circle'
    try:
        test = input_dict['plot_range_x_min']
    except:
        input_dict['plot_range_x_min'] = -4.0
    try:
        test = input_dict['plot_range_x_max']
    except:
        input_dict['plot_range_x_max'] = 4.0
    try:
        test = input_dict['plot_range_y_min']
    except:
        input_dict['plot_range_y_min'] = -4.0
    try:
        test = input_dict['plot_range_y_max']
    except:
        input_dict['plot_range_y_max'] = 4.0
    try:
        test = input_dict['dd_scale']
    except:
        input_dict['dd_scale'] = 1.0
    try:
        test = input_dict['anneal_temperature']
    except:
        input_dict['anneal_temperature'] = 0.0

    return input_dict

if __name__ == '__main__':
    
    #Read in parameters from input file
    input_dict = read_input(sys.argv[1])
    
    #Read data model files
    potential = am.lammps.Potential(input_dict['potential_file'], input_dict['potential_dir'])
    prototype = am.tools.Prototype(input_dict['prototype_file'])
    phase = am.tools.CrystalPhase(input_dict['phase_file'])
    dislocations = am.tools.DislocationMonopole(input_dict['dislocation_file'])
    
    #basic run parameters
    lammps_exe =  input_dict['lammps_exe']
    temperature = input_dict['anneal_temperature']
    dd_scale =    [input_dict['dd_scale']]
    system_size = [input_dict['system_size_x'], input_dict['system_size_y'], input_dict['system_size_z']]
    disl_type =   input_dict['dislocation_type']
    
    #Crystal phase dependent run parameters
    alat = phase.get('alat')
    cij =  phase.get('cij')
    symbols = []
    for element in phase.get('elements'):
        symbols.append(element['element'])
    ucell = prototype.ucell(a=alat[0], b=alat[1], c=alat[2], alpha=90, beta=90, gamma=90)
    b_width = alat[0] * input_dict['boundary_width']
    
    #Potential dependent run parameters
    units = potential.units()
    atom_style = potential.atom_style()
    pair_info = potential.pair_info(symbols)
    
    #Dislocation dependent run parameters
    axes =    dislocations.get(disl_type, 'axes')
    shift =   dislocations.get(disl_type, 'shift')
    burgers = alat[0] * np.array(dislocations.get(disl_type, 'burgers')) 
    cutoff =  alat[0] * dislocations.get('Nye_cutoff')
    tmax =    dislocations.get('Nye_angle')
    p = []
    for pset in dislocations.get('Nye_p'):
        p.append(alat[0] * pset)    
    plot_range = alat[0] * np.array([[input_dict['plot_range_x_min'], input_dict['plot_range_x_max']], 
                                     [input_dict['plot_range_y_min'], input_dict['plot_range_y_max']], 
                                      dislocations.get(disl_type, 'zwidth')                         ])
    
    #Define unique name
    fheader = 'disl--' + str(potential) + '--' + prototype.get('tag') + '-'
    for symbol in symbols:
        fheader += '-' + symbol
    fheader += '--' + disl_type
    
    #Get transformation matrix, T, and axes magnitudes
    T, ax_mag = am.tools.axes_check(axes)
    
    #Set system size parameters
    s = np.zeros(3, dtype=np.int)
    for i in xrange(3):
        scale = ceil(system_size[i] / ax_mag[i])
        if scale % 2 == 1:
            scale += 1
        s[i] = scale / 2
    size = np.array( [[-s[0], s[0]], [-s[1], s[1]], [-s[2], s[2]]], dtype=np.int )
    
    #Create and move to temporary directory  
    starting_dir = os.getcwd()    
    temp_dir = tempfile.mkdtemp(dir=starting_dir)
    os.chdir(temp_dir)
    
    #Build dislocation-free system
    base_file = fheader + '--base.dump' 
    system_info = am.lammps.sys_gen(units =       units,
                                    atom_style =  atom_style,
                                    pbc =         (False, False, True),
                                    ucell_box =   ucell.box(),
                                    ucell_atoms = ucell.atoms(scale=True),
                                    axes =        axes,
                                    shift =       shift,
                                    size =        size)

    sys0 = am.lammps.create_sys(lammps_exe, system_info)
    am.lammps.write_dump(base_file, sys0)  
    
    #Transform Burgers vector and elastic constant matrix
    b = T.dot(burgers)
    C = c_transform( c_mn_to_c_ijkl(cij), T)

    #Run Stroh calculations
    strohdata = stroh_setup(C)
    pre_ln = stroh_preln(b, strohdata)
    for i in xrange(sys0.natoms()):
        pos_x = sys0.atoms(i, 'pos', 0)
        pos_y = sys0.atoms(i, 'pos', 1)
        
        disp = stroh_disp_point(pos_x, pos_y, b, strohdata)
        stress = stroh_stress_point(pos_x, pos_y, b, C, strohdata)
        
        sys0.atoms(i, 'Stroh_displacement', disp)
        sys0.atoms(i, 'Stroh_stress', stress)

    am.lammps.write_dump(base_file, sys0)
    
    #Create dislocation system, sys1
    sys1 = deepcopy(sys0)
    for i in xrange(sys0.natoms()):
        newpos = sys0.atoms(i, 'pos') + sys0.atoms(i, 'Stroh_displacement')
        sys1.atoms(i, 'pos', newpos)

    #Apply boundary conditions
    boundaryfix(sys1, b_width, 'circle')
    moving_atypes = []
    for i in xrange(len(symbols)):
        moving_atypes.append(i+1)
    symbols += symbols 
    sys1.wrap()

    #Relax system
    pair_info = potential.pair_info(symbols)
    system_info = am.lammps.write_data('disl.dat', sys1, units=units, atom_style=atom_style)

    with open('disl_relax.in', 'w') as f:
        f.write(disl_relax_script(system_info, pair_info, moving_atypes, temp=temperature))

    disl_file = fheader + '--disl.dump'
    data = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in disl_relax.in',shell=True))
    sys1 = am.lammps.read_dump('atom.'+data[-1][0])
    am.lammps.write_dump(disl_file, sys1)
    
    #Calculate nearest neighbor lists
    sys0.neighbors(cutoff)
    sys1.neighbors(cutoff)
    
    #Calculate differential displacement plot
    dd(sys0, sys1, plot_range, b, scale=dd_scale, save=True)
    
    #Calculate Nye tensor
    sys1.prop('axes', axes)
    nye(sys1, p, tmax)
    
    #Plot results from Nye tensor calculation
    bx, avsum = a2cplot(sys1, 'Nye', 2, 0, plotbounds=plot_range, save=True)
    by, avsum = a2cplot(sys1, 'Nye', 2, 1, plotbounds=plot_range, save=True)
    bz, avsum = a2cplot(sys1, 'Nye', 2, 2, plotbounds=plot_range, save=True)
    
    #Copy dump files out of temp folder and delete temp folder
    os.chdir(starting_dir)
    for fname in os.listdir(temp_dir):
        if fname[-5:] == '.dump':
            try:
                os.rename(os.path.join(temp_dir,fname), fname)
            except:
                os.remove(fname)
                os.rename(os.path.join(temp_dir,fname), fname)
        elif fname[-4:] == '.png': 
            try:
                os.rename(os.path.join(temp_dir,fname), fheader + '--' + fname)
            except:
                os.remove(fheader + '--' + fname)
                os.rename(os.path.join(temp_dir,fname), fheader + '--' + fname)
        else:
            os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    json_data = OrderedDict()
    json_data['calculationDislocationMonopole'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = str(potential)
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = prototype.get('tag')
    
    #Add defect name
    sim['dislocationMonopoleID'] = OrderedDict()
    sim['dislocationMonopoleID']['dislocationTag'] = disl_type
    
    #Add pre-ln energy factor
    sim['pre-lnEnergyFactor'] = OrderedDict([( 'value', pre_ln),
                                              ( 'unit',  'eV')       ])
    
    #Add Nye tensor estimate of the Burgers vector
    b_est = [float('%.3f' % bx), float('%.3f' % by), float('%.3f' % bz)]
    sim['nyeBurgersEstimate'] = b_est                                   

    with open(fheader+'.json', 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    