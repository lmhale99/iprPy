#!/usr/bin/env python2.7

# Standard library imports
import os
import subprocess
from copy import deepcopy
import sys
import tempfile
import json
from collections import OrderedDict
import uuid

#Additional imports
import numpy as np

#Custom imports
import atomman as am
from atomman.tools import mag

def alat_script(system_info, pair_info, delta = 1e-5, steps = 2):
#Create a LAMMPS script that applies a hydrostatic strain.    
    nl = '\n'
    script = nl.join([system_info,
                      '',
                      pair_info,
                      '',
                      'variable lx0 equal lx',
                      'variable ly0 equal ly',
                      'variable lz0 equal lz',
                      '',
                      'variable deltax equal %f/%f' % (delta, steps-1),
                      'variable aratio equal 1-%f/2.+(v_a-1)*${deltax}' % (delta),
                      '',
                      'variable xmax equal v_aratio*${lx0}',
                      'variable ymax equal v_aratio*${ly0}',
                      'variable zmax equal v_aratio*${lz0}',
                      '',
                      'variable peatom equal pe/atoms',
                      'thermo_style custom step lx ly lz pxx pyy pzz v_peatom pe',
                      'thermo_modify format float %.13e',
                      '',
                      'label loop',
                      '',
                      'variable a loop %i' % (steps),
                      'change_box all x final 0 ${xmax} y final 0 ${ymax} z final 0 ${zmax} remap units box',
                      'run 0',
                      'next a','jump alat.in loop'])
    return script        

def cij_script(system_info, pair_info, delta = 1e-5, steps = 2):
#Create lammps script that strains a crystal in each direction x,y,z and shear yz,xz,xy independently.    
        
    nl = '\n'
    script = nl.join([system_info,
                      '',
                      pair_info,
                      '',
                      'variable lx0 equal $(lx)',
                      'variable ly0 equal $(ly)',
                      'variable lz0 equal $(lz)',
                      '',
                      'variable deltax equal %f/%f'%(delta, steps-1),
                      '',
                      'variable peatom equal pe/atoms',
                      'thermo_style custom step lx ly lz yz xz xy pxx pyy pzz pyz pxz pxy v_peatom pe',
                      'thermo_modify format float %.13e',
                      '',
                      'run 0',
                      '',
                      'variable aratio equal 1-%f/2.+(v_a-1)*${deltax}'%(delta),
                      'variable xmax equal v_aratio*${lx0}',
                      'label loopa',
                      'variable a loop %i'%(steps),
                      'change_box all x final 0 ${xmax} remap units box',
                      'run 0',
                      'next a','jump cij.in loopa',
                      'change_box all x final 0 ${lx0} remap units box',
                      '',
                      'variable bratio equal 1-%f/2.+(v_b-1)*${deltax}'%(delta),
                      'variable ymax equal v_bratio*${ly0}',
                      'label loopb',
                      'variable b loop %i'%(steps),
                      'change_box all y final 0 ${ymax} remap units box',
                      'run 0',
                      'next b','jump cij.in loopb',
                      'change_box all y final 0 ${ly0} remap units box',
                      '',
                      'variable cratio equal 1-%f/2.+(v_c-1)*${deltax}'%(delta),
                      'variable zmax equal v_cratio*${lz0}',
                      'label loopc',
                      'variable c loop %i'%(steps),
                      'change_box all z final 0 ${zmax} remap units box',
                      'run 0',
                      'next c','jump cij.in loopc',
                      'change_box all z final 0 ${lz0} remap units box',
                      '',
                      'change_box all triclinic',
                      'variable eyz equal (-%f/2.+(v_d-1)*${deltax})*${lz0}'%(delta),
                      'label loopd',
                      'variable d loop %i'%(steps),
                      'change_box all yz final ${eyz} remap units box',
                      'run 0',
                      'next d','jump cij.in loopd',
                      'change_box all yz final 0 remap units box',
                      '',
                      'variable exz equal (-%f/2.+(v_e-1)*${deltax})*${lz0}'%(delta),
                      'label loope',
                      'variable e loop %i'%(steps),
                      'change_box all xz final ${exz} remap units box',
                      'run 0',
                      'next e','jump cij.in loope',
                      'change_box all xz final 0 remap units box',
                      '',
                      'variable exy equal (-%f/2.+(v_f-1)*${deltax})*${ly0}'%(delta),
                      'label loopf',
                      'variable f loop %i'%(steps),
                      'change_box all xy final ${exy} remap units box',
                      'run 0',
                      'next f','jump cij.in loopf',
                      'change_box all xy final 0 remap units box'])
    return script   

def cij_vs_p(lammps_exe, ucell, potential, symbols, delta = 0.1, steps = 200):
#Computes the pressure dependent elastic constants in strain range "delta" for "steps" number of points   
    
    #initial parameter definitions
    pvalues = np.empty((steps))
    C11 = np.empty((steps))
    C22 = np.empty((steps))
    C33 = np.empty((steps))
    C12 = np.empty((steps))
    C13 = np.empty((steps))
    C23 = np.empty((steps))
    C44 = np.empty((steps))
    C55 = np.empty((steps))
    C66 = np.empty((steps))
    dimensions = np.empty((13,6))       
    stresses = np.empty((13,6))
    
    #LAMMPS script setup
    pair_info = potential.pair_info(symbols)
    
    system_info = am.lammps.sys_gen(units =       potential.units(),
                                    atom_style =  potential.atom_style(),
                                    ucell_box =   ucell.box(),
                                    ucell_atoms = ucell.atoms(scale=True),
                                    size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))
    
    with open('alat.in','w') as f:
        f.write(alat_script(system_info, pair_info, delta=delta, steps=steps))
    data1 = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in alat.in', shell=True))
    
    #Extract pressures and associated lattice parameters
    for c in xrange(steps):
        newbox = am.Box(a = float(data1[c+1][1]) / 3.,
                        b = float(data1[c+1][2]) / 3.,
                        c = float(data1[c+1][3]) / 3.)
        
        pvalues[c] = ((float(data1[c+1][4]) + float(data1[c+1][5]) + float(data1[c+1][6])) / 3. ) * 1e-4
        
        system_info = am.lammps.sys_gen(units =       potential.units(),
                                        atom_style =  potential.atom_style(),
                                        ucell_box =   newbox,
                                        ucell_atoms = ucell.atoms(scale=True),
                                        size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))
        
        with open('cij.in','w') as f:
            f.write(cij_script(system_info, pair_info))
            
        data2 = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in cij.in', shell=True))
 
        #Extract system dimensions and pressures from LAMMPS data output
        for q in xrange(13):
            for p in xrange(6):
                dimensions[q, p] = float(data2[q+1][p+1])
                stresses[q, p] = -float(data2[q+1][p+7])*1e-4
        eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                              dimensions[0,2], dimensions[0,2], dimensions[0,1]])

        #Calculate Cij from LAMMPS results
        cij = np.empty((6,6))
        for i in xrange(0,6):
            eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]  
            for j in xrange(0,6):
                sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                cij[j,i] = sig_ij/eps_ij
        
        C11[c] = cij[0,0]
        C22[c] = cij[1,1]
        C33[c] = cij[2,2]
        C12[c] = cij[0,1]
        C13[c] = cij[0,2]
        C23[c] = cij[1,2]
        C44[c] = cij[3,3]
        C55[c] = cij[4,4]
        C66[c] = cij[5,5]
    
    return {'p':pvalues, 'C11':C11,'C22':C22,'C33':C33,
                         'C12':C12,'C13':C13,'C23':C23,
                         'C44':C44,'C55':C55,'C66':C66}
    
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
                elif terms[0] == 'delta':
                    input_dict['delta'] = float(terms[1])
                elif terms[0] == 'steps':
                    input_dict['steps'] = int(terms[1])
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
        test = input_dict['delta']
    except:
        input_dict['delta'] = 0.1
    try:
        test = input_dict['steps']
    except:
        input_dict['steps'] = 100

    return input_dict

  
if __name__ == '__main__':
    
    #Read in parameters from input file
    input_dict = read_input(sys.argv[1])
    
    #Read data model files
    potential = am.lammps.Potential(input_dict['potential_file'], input_dict['potential_dir'])
    prototype = am.tools.Prototype(input_dict['prototype_file'])
    phase = am.tools.CrystalPhase(input_dict['phase_file'])
    
    #Set run parameters
    lammps_exe = input_dict['lammps_exe']
    delta = input_dict['delta']
    steps = input_dict['steps']
    
    alat = phase.get('alat')
    symbols = []
    for element in phase.get('elements'):
        symbols.append(element['element'])
    ucell = prototype.ucell(a=alat[0], b=alat[1], c=alat[2], alpha=90, beta=90, gamma=90)

    #Create and move to temporary directory  
    starting_dir = os.getcwd()    
    temp_dir = tempfile.mkdtemp(dir=starting_dir)
    os.chdir(temp_dir)
    
    #Perform the Cij vs P calculation    
    values = cij_vs_p(lammps_exe, ucell, potential, symbols, delta = delta, steps = steps)
    
    fheader = 'CijvsP--' + str(potential) + '--' + prototype.get('tag') + '-'
    for symbol in symbols:
        fheader += '-' + symbol
    
    #Copy dump files out of temp folder and delete temp folder
    os.chdir(starting_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    #Create and write data model
    json_data = OrderedDict()
    json_data['calculationPressureDependentElasticConstants'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = potential.get('id')
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = prototype.get('tag')
    
    #Add elastic constant plot information
    sim['elasticConstantRelation'] = OrderedDict([('point', [] )])
    
    for i in xrange(len(values['p'])):
        point = OrderedDict()
        point['P'] = OrderedDict([( 'value', values['p'][i] ),
                                  ( 'unit', 'GPa' )])
        point['C11'] = OrderedDict([( 'value', values['C11'][i] ),
                                    ( 'unit', 'GPa' )])   
        point['C22'] = OrderedDict([( 'value', values['C22'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C33'] = OrderedDict([( 'value', values['C33'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C12'] = OrderedDict([( 'value', values['C12'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C13'] = OrderedDict([( 'value', values['C13'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C23'] = OrderedDict([( 'value', values['C23'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C44'] = OrderedDict([( 'value', values['C44'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C55'] = OrderedDict([( 'value', values['C55'][i] ),
                                    ( 'unit', 'GPa' )]) 
        point['C66'] = OrderedDict([( 'value', values['C66'][i] ),
                                    ( 'unit', 'GPa' )])  
        sim['elasticConstantRelation']['point'].append(point)

    with open(fheader+'.json', 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    