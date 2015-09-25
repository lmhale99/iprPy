#!/usr/bin/env python2.7

# Standard library imports
import os
import subprocess
import json
from collections import OrderedDict
import uuid
import sys
from copy import deepcopy
import tempfile
from math import ceil

#Additional imports
import numpy as np

#Custom imports
import iprp
import iprp.lammps as lmp
import iprp.models as dm
from iprp.calcs import *
from iprp.calcs.scripts import disl_relax_script

mappit = map

def main(argv):
    #Check for and read in listed input script
    if len(argv) == 1:
        raise RuntimeError('No input file specified')
    inputs = read_input(argv[1])
    
    #Initialize parameters (used for testing all necessary inputs supplied)
    lammps_exe = None
    ipr_dir = os.getcwd()
    potentials = []
    crystals = []
    
    #loop over input lines
    for input in inputs:
        #lammps_exe input line
        if input[0] == 'lammps_exe':
            if len(input) > 1:
                lammps_exe = input[1]
                for i in xrange(2,len(input)):
                    lammps_exe += ' ' + input[i]
            else:
                raise RuntimeError('Invalid lammps_exe command')
        
        #ipr_dir input line
        elif input[0] == 'ipr_dir':
            if len(input) > 1:
                ipr_dir = input[1]
                for i in xrange(2,len(input)):
                    ipr_dir += ' ' + input[i]
            else:
                raise RuntimeError('Invalid ipr_dir command')
                
        #potential input line
        elif input[0] == 'potential':
            potentials = read_potentials(input[1:], ipr_dir)
            
        #crystal input line
        elif input[0] == 'crystal':
            crystals = read_crystals(input[1:], ipr_dir, crystals)
            
        #run_0K_structure input line
        elif input[0] == 'run_0K_structure':
            run_0K_structure(input[1:], lammps_exe, ipr_dir, potentials)
            
        #run_Cij_vs_P input line
        elif input[0] == 'run_Cij_vs_P':
            run_Cij_vs_P(input[1:], lammps_exe, ipr_dir, potentials, crystals)
        
        #run_point_defect input line
        elif input[0] == 'run_point_defect':
            run_point_defect(input[1:], lammps_exe, ipr_dir, potentials, crystals)
            
        #run_point_defect input line
        elif input[0] == 'run_dislocation':
            run_dislocation(input[1:], lammps_exe, ipr_dir, potentials, crystals)
            
        else:
            raise RuntimeError('Unknown command %s' % input[0])
            
   
#Read in listed inputs from input script    
def read_input(fname):
    inputs = []
    if True:
    #try:
        with open(fname) as dr_file:
            for line in dr_file:
                terms = line.split()
                if len(terms) > 0 and terms[0][0] != '#':
                    inputs.append(terms)
    else:
    #except:
        print 'Error reading ' + fname
        sys.exit()
    
    return inputs

#Read in all data for running potentials in LAMMPS     
def read_potentials(terms, ipr_dir):
    if len(terms) == 1 and terms[0] == 'all':
        style = 'all'
    elif len(terms) > 1 and terms[0] == 'name':
        style = 'name'
        arg_list = terms[1:]
    elif len(terms) > 1 and terms[0] == 'element':
        style = 'element'
        arg_list = terms[1:]
    else:
        raise RuntimeError('Invalid potential command')
    
    pot_dir = os.path.join(ipr_dir,'ref','potentialInstances-LAMMPS')
    file_dir = os.path.join(ipr_dir,'ref','potentials')
    potentials = []
        
    #loop over all files in potentialInstances_LAMMPS directory pot_dir
    flist = os.listdir(pot_dir)
    for fname in flist:
        if fname[-5:] == '.json':
            
            #try reading .json file and save as pot = iprp.lammps.Potential
            try:
                pot = iprp.lammps.Potential(os.path.join(pot_dir,fname), os.path.join(file_dir,fname[:-5]))    
            except:
                print 'Failed to properly read '+os.path.join(pot_dir,fname)
                continue
            
            pot_id = str(pot)

            #if 'run all' add every potential to potentials
            if style == 'all':
                potentials.append(pot)

            #if 'run potential' only add listed potentials to potentials
            elif style == 'name':
                for pot_name in arg_list:
                    if pot_name == pot.get('id'):
                        potentials.append(pot)
                        break

            #if 'run element' only add potentials with listed elements to potentials           
            elif style == 'element':
                found = False
                elist = pot.elements()
                for e1 in elist:
                    for e2 in arg_list:
                        if e1 == e2:
                            potentials.append(pot)
                            found = True
                            break
                    if found: break

    return potentials
    
#Read in all data associated with a crystal structure    
def read_crystals(terms, ipr_dir, crystals):
    proto_dir = os.path.join(ipr_dir,'ref','crystalPrototypes')
    
    if len(terms) == 1 and terms[0] == 'clear':
        return []
        
    elif len(terms) >= 5 and terms[0] == 'add':
        new_crystal = {}
        if terms[1] == 'prototype' and terms[3] == 'elements':
            proto_id = terms[2]
            elements = terms[4:]
            found = False
            
            flist = os.listdir(proto_dir)
            for fname in flist:
                if fname[-5:] == '.json':
                    try:  
                        cdata = iprp.models.CrystalPrototype( os.path.join(proto_dir, fname) )
                        if cdata.isid(proto_id):
                            new_crystal['proto'] = cdata
                            found = True
                            break
                    except:
                        print 'Failed to properly read ' + os.path.join(proto_dir, fname)
                        continue
            if found:
                if len(elements) == new_crystal['proto'].get('nsites'):
                    new_crystal['elements'] = elements
                    crystals.append(new_crystal)
                    return crystals    
                else:
                    raise RuntimeError('Invalid crystal command: #elements != #sites')
            else:
                raise RuntimeError('Invalid crystal command: unknown prototype name %s' % proto_id)
        else:
            raise RuntimeError('Invalid crystal command')    
    else:
        raise RuntimeError('Invalid crystal command')
        
#Setup and run the static structure calculations
def run_0K_structure(terms, lammps_exe, ipr_dir, potentials):
    print 'run_0K_structure'
    
    cwd = os.getcwd()
    try:
        os.chdir(   os.path.join(ipr_dir,'results','json','struct'))
        os.chdir(cwd)
    except:
        os.makedirs(os.path.join(ipr_dir,'results','json','struct'))
    
    proto_dir = os.path.join(ipr_dir,'ref','crystalPrototypes')
    
    #Set default r_range values
    r_min = 2.0
    r_max = 5.0
    r_step = 200
    
    #Read in all crystal prototypes in proto_dir
    protos = []
    flist = os.listdir(proto_dir)
    for fname in flist:
        if fname[-5:] == '.json':
            try:  
                cdata = iprp.models.CrystalPrototype( os.path.join(proto_dir, fname) )
                protos.append(cdata)
            except:
                print 'Failed to properly read ' + os.path.join(proto_dir, fname)
                continue
    
    #Parse run_0K_structure arguments
    while len(terms) > 0:
        #set r_range 
        if terms[0] == 'r_range':
            try:
                r_min = float(terms[1])
                r_max = float(terms[2])
                r_step = int(terms[3])
                terms = terms[4:]
            except:
                raise RuntimeError('Invalid run_0K_structure command: r_range')
        
        elif terms[0] == 'prototypes':
            if terms[1] == 'all':
                terms = terms[2:]
            elif terms[1] == 'name':
                try:
                    endex = terms.index('r_range')
                    names = terms[2:endex]
                    terms = terms[endex:]
                except:
                    names = terms[2:]
                    terms = []
                if len(names) > 0:
                    short_protos = []
                    for name in names:
                        for proto in protos:
                            if proto.isid(name):
                                short_protos.append(proto)
                                break
                    if len(names) == len(short_protos):
                        protos = short_protos
                    else:
                        raise RuntimeError('Invalid run_0K_structure command: not all prototypes found')
                else:
                    raise RuntimeError('Invalid run_0K_structure command: prototypes name')
            else:
                raise RuntimeError('Invalid run_0K_structure command: prototypes')
        else:
            raise RuntimeError('Invalid run_0K_structure command')
    
    npots = len(potentials)
    i_lammps_exe = [lammps_exe for i in xrange(npots)]
    i_ipr_dir =    [ipr_dir    for i in xrange(npots)]
    i_protos =     [protos     for i in xrange(npots)]   
    i_r_min =      [r_min      for i in xrange(npots)]
    i_r_max =      [r_max      for i in xrange(npots)]
    i_r_step =     [r_step     for i in xrange(npots)]

    mappit(iter_0K_structure, i_lammps_exe, i_ipr_dir, potentials, i_protos, i_r_min, i_r_max, i_r_step)

#Isolated calculation packet    
def iter_0K_structure(lammps_exe, ipr_dir, potential, protos, r_min, r_max, r_step):
    #Go to simulation directory
    pot_id = potential.get('id')

    #Create simulation output directory
    output_dir = os.path.join(ipr_dir, 'results', 'sim', potential.get('id'), 'struct')     
    try:
        os.chdir(output_dir)
    except:
        os.makedirs(output_dir)
    
    #Create and move to temporary directory    
    temp_dir = tempfile.mkdtemp(dir=os.path.join(ipr_dir,'results','temp'))
    os.chdir(temp_dir)
    
    #Make list of all elements associated with the potential
    elem_list = potential.elements()
    mass_list = potential.masses()
    
    #Loop over prototypes
    for proto in protos:
        
        #Count how many atoms are in each unique prototype site
        quants = []
        for i in xrange(1, proto.get('nsites') + 1):
            count = 0
            for atom in proto.get('ucell'):
                if atom.get('type') == i:
                    count += 1
            quants.append(count)
            
        #Iterate over all element - site combinations    
        for index_array in iterbox( len(elem_list), proto.get('nsites') ):
            results = iprp.models.CrystalPhase()
            results.set_pot_name(potential.get('id'))
            
            #Build lists of elements and masses, and out_file name
            elements = []
            masses = []
            out_file = proto.get('tag') + '-'
            for el_index in index_array:
                elements.append(      elem_list[el_index])
                masses.append(        mass_list[el_index])
                out_file += '-' + str(elem_list[el_index])
            
            rvals, avals, evals = e_plot(lammps_exe, potential, elements, masses, proto, rmin=r_min, rmax=r_max, rsteps=r_step)
            
            results.set_E_vs_r_data(rvals, avals, evals)
            
            with open(os.path.join(output_dir, out_file + '.dat'), 'w') as fout:
                fout.write('Dependence of the cohesive energy on lattice parameter, a, and nearest neighbor distance, r\n')
                fout.write('r(A) a(A) Ecoh(eV)\n')
                for i in xrange(len(evals)):
                    fout.write('%f %f %f\n' % (rvals[i], avals[i], evals[i]))
            
            mindex = np.argmin(evals)
            atest = avals[mindex]
            alat0 = atest*proto.get('lat_mult')
            
            try:
                adata = refine_lat(lammps_exe, potential, elements, masses, proto, alat0)
                test = adata['ecoh']
            except:
                break
            
            b_mod = bulk_mod(lammps_exe, potential, elements, masses, proto, adata['alat'])
            
            results.set_sim_data(elements, proto, adata['ecoh'], adata['alat'], b_mod, adata['cij'])
            json_name = 'struct--' + potential.get('id') + '--' + out_file + '.json'
            results.dump( os.path.join(ipr_dir, 'results', 'json', 'struct', json_name) ) 
    
    #Clear and delete temporary directory
    os.chdir(ipr_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    table_structs(ipr_dir, potential)

#Setup and run the pressure dependent elastic constant calculations    
def run_Cij_vs_P(terms, lammps_exe, ipr_dir, potentials, crystals):
    print 'run_Cij_vs_P'
    
    cwd = os.getcwd()
    try:
        os.chdir(   os.path.join(ipr_dir,'results','json','CijvsP'))
        os.chdir(cwd)
    except:
        os.makedirs(os.path.join(ipr_dir,'results','json','CijvsP'))
    
    #Set default strain and steps values
    strain = 0.1
    steps = 200
    
    #Parse run_Cij_vs_P arguments
    while len(terms) > 0:
        #set strain
        if terms[0] == 'strain':
            try:
                strain = float(terms[1])
                terms = terms[2:]
            except:
                raise RuntimeError('Invalid run_Cij_vs_P command: strain')
        elif terms[0] == 'steps':
            try:
                steps = int(terms[1])
                terms = terms[2:]
            except:
                raise RuntimeError('Invalid run_Cij_vs_P command: steps')
        else:
            raise RuntimeError('Invalid run_Cij_vs_P command')
    
    i_potential = []
    i_crystal = []    
    i_phase = []
    struct_dir = os.path.join(ipr_dir, 'results', 'json', 'struct')
    
    for potential in potentials:
        for crystal in crystals:
            json_name = 'struct--' + potential.get('id') + '--' + crystal['proto'].get('tag') + '-'
            for element in crystal['elements']:
                json_name += '-' + element
            json_name += '.json'
            
            try:
                phase = iprp.models.CrystalPhase(os.path.join(struct_dir, json_name))
                i_potential.append(potential)
                i_crystal.append(crystal)
                i_phase.append(phase)
            except:
                print 'Could not find ' + json_name
    
    nsims = len(i_phase)
    i_lammps_exe = [lammps_exe for i in xrange(nsims)]
    i_ipr_dir =    [ipr_dir    for i in xrange(nsims)]
    i_strain =     [strain     for i in xrange(nsims)]
    i_steps =      [steps      for i in xrange(nsims)]
    
    mappit(iter_Cij_vs_P, i_lammps_exe, i_ipr_dir, i_potential, i_crystal, i_phase, i_strain, i_steps)

#Isolated calculation packet
def iter_Cij_vs_P(lammps_exe, ipr_dir, potential, crystal, phase, strain, steps):
    #Set run parameters
    proto = crystal['proto']
    elements = crystal['elements']
    masses = potential.masses(elements)
    alat = phase.get('alat')
    
    #Create simulation output directory
    output_dir = os.path.join(ipr_dir, 'results', 'sim', potential.get('id'), 'CijvsP')     
    try:
        os.chdir(output_dir)
    except:
        os.makedirs(output_dir)
    
    #Create and move to temporary directory    
    temp_dir = tempfile.mkdtemp(dir=os.path.join(ipr_dir,'results','temp'))
    os.chdir(temp_dir)
    
    values = cij_vs_p(lammps_exe, potential, elements, masses, proto, alat, delta=strain, steps=steps)
   
    #Clear and delete temporary directory
    os.chdir(ipr_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    out_file = proto.get('tag') + '-'
    for element in elements:
        out_file += '-' + element
        
    with open(os.path.join(output_dir, out_file + '.dat'), 'w') as fout:
        fout.write('Dependence of the elastic constants, Cij, on hydrostatic pressure, P. All Values in GPa\n')
        fout.write('P C11 C22 C33 C12 C13 C23 C44 C55 C66\n')
        for i in xrange(len(values['p'])):
            fout.write('%f %f %f %f %f %f %f %f %f %f\n' % (values['p'][i],
                                                            values['C11'][i], values['C22'][i], values['C33'][i],
                                                            values['C12'][i], values['C13'][i], values['C23'][i],
                                                            values['C44'][i], values['C55'][i], values['C66'][i]))
        
    
    json_file = 'CijvsP--' + potential.get('id') + '--' + out_file + '.json'
    json_dir = os.path.join(ipr_dir,'results','json','CijvsP')
    
    json_data = OrderedDict()
    json_data['calculationPressureDependentElasticConstants'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = potential.get('id')
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = proto.get('tag')
    
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
    
    with open(os.path.join(json_dir, json_file), 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))

#Setup and run the point defect formation energy calculations    
def run_point_defect(terms, lammps_exe, ipr_dir, potentials, crystals):
    print 'run_point_defect'
    
    cwd = os.getcwd()
    try:
        os.chdir(   os.path.join(ipr_dir,'results','json','ptd'))
        os.chdir(cwd)
    except:
        os.makedirs(os.path.join(ipr_dir,'results','json','ptd'))
    
    #Set default strain and steps values
    min_size = 4
    max_size = 10
    
    #Build library of point defects
    ptds = []
    ptd_dir = os.path.join(ipr_dir,'ref','pointDefects')
    flist = os.listdir(ptd_dir)
    for fname in flist:
        if fname[-5:] == '.json':
            try:  
                ddata = iprp.models.PointDefect( os.path.join(ptd_dir, fname) )
            except:
                print 'Failed to properly read ' + os.path.join(ptd_dir, fname)
                continue
            
            proto_name = ddata.get('prototype')
            for tag in ddata.get('list'):
                ptd = {'proto': proto_name,
                       'tag': tag,
                       'name': ddata.get(tag,'name'),
                       'params': ddata.get(tag,'parameters')}
                ptds.append(ptd)   
    
    #Parse run_point_defect arguments
    while len(terms) > 0:
        #set strain
        if terms[0] == 'size_range':
            try:
                min_size = int(terms[1])
                max_size = int(terms[2])
                terms = terms[3:]
                if min_size%2 == 1 or max_size%2 == 1:
                    raise RuntimeError('Invalid run_point_defect command: sizes must be even')
            except:
                raise RuntimeError('Invalid run_point_defect command: size_range')
        elif terms[0] == 'types':
            if terms[1] == 'all':
                terms = terms[2:]
            elif terms[1] == 'list':
                try:
                    endex = terms.index('size_range')
                    names = terms[2:endex]
                    terms = terms[endex:]
                except:
                    names = terms[2:]
                    terms = []
                if len(names) > 0:
                    short_ptds = []
                    for name in names:
                        for ptd in ptds:
                            if ptd['tag'] == name:
                                short_ptds.append(ptd)
                    ptds = short_ptds
                else:
                    raise RuntimeError('Invalid run_point_defect command: types list')
            else:
                raise RuntimeError('Invalid run_point_defect command: types')
        else:
            raise RuntimeError('Invalid run_point_defect command')
    
    i_potential = []
    i_crystal = []    
    i_phase = []
    i_ptd = []
    struct_dir = os.path.join(ipr_dir, 'results', 'json', 'struct')
    
    for potential in potentials:
        for crystal in crystals:
            json_name = 'struct--' + potential.get('id') + '--' + crystal['proto'].get('tag') + '-'
            for element in crystal['elements']:
                json_name += '-' + element
            json_name += '.json'
            
            try:
                phase = iprp.models.CrystalPhase(os.path.join(struct_dir, json_name))
            except:
                print 'Could not find ' + json_name
                continue
            
            #See if point defect corresponds to crystal prototype
            for ptd in ptds:
                if ptd['proto'] == crystal['proto'].get('tag'):
                    i_potential.append(potential)
                    i_crystal.append(crystal)
                    i_phase.append(phase)
                    i_ptd.append(ptd)
                    
    nsims = len(i_phase)
    i_lammps_exe = [lammps_exe for i in xrange(nsims)]
    i_ipr_dir =    [ipr_dir    for i in xrange(nsims)]
    i_min_size =   [min_size   for i in xrange(nsims)]
    i_max_size =   [max_size   for i in xrange(nsims)]
    
    mappit(iter_point_defect, i_lammps_exe, i_ipr_dir, i_potential, i_crystal, i_phase, i_ptd, i_min_size, i_max_size)

#Isolated calculation packet
def iter_point_defect(lammps_exe, ipr_dir, potential, crystal, phase, ptd, min_size, max_size):
    #Set run parameters
    proto = crystal['proto']
    elements = crystal['elements']
    masses = potential.masses(elements)
    alat = phase.get('alat')
    ptd_params = ptd['params']
    ptd_tag = ptd['tag']
   
    #Create simulation output directory
    output_dir = os.path.join(ipr_dir, 'results', 'sim', potential.get('id'), 'ptd')     
    try:
        os.chdir(output_dir)
    except:
        os.makedirs(output_dir)
    
    #Create and move to temporary directory    
    temp_dir = tempfile.mkdtemp(dir=os.path.join(ipr_dir,'results','temp'))
    os.chdir(temp_dir)
    
    natoms, energies, centro, rcoord = ptd_energy(lammps_exe, potential, elements, masses, proto, alat, ptd_params, 
                                                  output_dir=output_dir, ptd_tag=ptd_tag, min_size=min_size, max_size=max_size)
    
    #Clear and delete temporary directory
    os.chdir(ipr_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
   
    #Make list of energies for stable defect systems
    invatoms_list = []
    energies_list = []
    for i in xrange(len(natoms)): 
        if (np.allclose(centro[i], np.zeros(3), rtol=0, atol=1e-3) and
            np.allclose(rcoord[i], np.zeros(3), rtol=0, atol=1e-3)):
            invatoms_list.append(1./natoms[i])
            energies_list.append(energies[i])
            
    #If no stable energies found
    if len(energies_list)==0:
        defect_energy = 'Unstable'
    #If stable energies found
    else:
        xlist = np.linspace(0,max(invatoms_list))
        defect_energy = energies_list[0]
        if len(energies_list)==2:
            m1,b = np.polyfit(invatoms_list, energies_list, 1)
            defect_energy = b
        elif len(energies_list)>2:
            m2,m1,b = np.polyfit(invatoms_list, energies_list, 2)
            defect_energy = b
            
    out_file = proto.get('tag') + '-'
    for element in elements:
        out_file += '-' + element
    out_file += '--' + ptd['tag']
        
    with open(os.path.join(output_dir, out_file + '.dat'),'w') as f:
        f.write('Point defect formation energies (eV) vs. system size\n')
        f.write('Calculations from the NIST Interatomic Potential Repository Project\n')
        f.write('%s %s %s %s\n' % (potential.get('id'), proto.get('tag'), phase.get('chem_formula'), ptd['tag']))
        f.write('  natoms E_formation(eV)           centrosummation        coordRelaxation\n')
        
        for i in xrange(len(natoms)):
            f.write('%8d    %-15.10f [%6.3f,%6.3f,%6.3f] [%6.3f,%6.3f,%6.3f]' % (natoms[i], energies[i],
                                                                            centro[i][0], centro[i][1], centro[i][2],
                                                                            rcoord[i][0], rcoord[i][1], rcoord[i][2]))
            if (np.allclose(centro[i], np.zeros(3), rtol=0, atol=1e-3) and
                np.allclose(rcoord[i], np.zeros(3), rtol=0, atol=1e-3)):
                f.write('\n')
            else:
                f.write(' Unstable\n')
            
    json_file = 'ptd--' + potential.get('id') + '--' + out_file + '.json'
    json_dir = os.path.join(ipr_dir,'results','json','ptd')
    
    json_data = OrderedDict()
    json_data['calculationPointDefects'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = potential.get('id')
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = proto.get('tag')
    
    #Add defect name
    sim['pointDefectID'] = OrderedDict()
    sim['pointDefectID']['pointDefectName'] = ptd['name']
    sim['pointDefectID']['pointDefectTag'] = ptd['tag']
    
    #Add extrapolated value
    sim['formationEnergy'] = OrderedDict([( 'value', defect_energy),
                                          ( 'unit',  'eV')       ])
    
    #Add calculation points
    sim['formationEnergyRelation'] = OrderedDict([('point', [] )])
    for i in xrange(len(energies)):
        point = OrderedDict()
        point['formationEnergy'] = OrderedDict([( 'value', energies[i]),
                                                ( 'unit',  'eV')        ])
        point['centrosummation'] = [float('%.3f'%centro[i][0]),
                                    float('%.3f'%centro[i][1]),
                                    float('%.3f'%centro[i][2])]
        point['coordRelaxation'] = [float('%.3f'%rcoord[i][0]),
                                    float('%.3f'%rcoord[i][1]),
                                    float('%.3f'%rcoord[i][2])]
        sim['formationEnergyRelation']['point'].append(point)
                                    

    with open(os.path.join(json_dir, json_file), 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))

#Setup and run the dislocation monopole calculations    
def run_dislocation(terms, lammps_exe, ipr_dir, potentials, crystals):
    print 'run_dislocation'
    
    cwd = os.getcwd()
    try:
        os.chdir(   os.path.join(ipr_dir,'results','json','disl'))
        os.chdir(cwd)
    except:
        os.makedirs(os.path.join(ipr_dir,'results','json','disl'))
    
    #Set default system size and temperature values
    size = np.array([40, 40, 1], dtype=np.int)
    temperature = 0
    xwidth = [-10, 10]
    ywidth = [-10, 10]
    
    #Build library of point defects
    disls = []
    disl_dir = os.path.join(ipr_dir, 'ref', 'dislocationMonopoles')
    flist = os.listdir(disl_dir)
    for fname in flist:
        if fname[-5:] == '.json':
            try:  
                ddata = iprp.models.DislocationMonopole( os.path.join(disl_dir, fname) )
            except:
                print 'Failed to properly read ' + os.path.join(disl_dir, fname)
                continue
            
            proto_name = ddata.get('prototype')
            for tag in ddata.get('list'):
                disl = {'proto': proto_name,
                       'tag': tag,
                       'data': ddata}
                disls.append(disl)   
    
    #Parse run_point_defect arguments
    while len(terms) > 0:
        #set strain
        if terms[0] == 'size':
            try:
                size[0] = float(terms[1])
                size[1] = float(terms[2])
                size[2] = float(terms[3])
                terms = terms[4:]
            except:
                raise RuntimeError('Invalid run_dislocation command: size')
        elif terms[0] == 'xwidth':
            try:
                xwidth[0] = float(terms[1])
                xwidth[1] = float(terms[2])
                terms = terms[3:]
            except:
                raise RuntimeError('Invalid run_dislocation command: xwidth')
        elif terms[0] == 'ywidth':
            try:
                ywidth[0] = float(terms[1])
                ywidth[1] = float(terms[2])
                terms = terms[3:]
            except:
                raise RuntimeError('Invalid run_dislocation command: ywidth')  
        elif terms[0] == 'temperature':
            try:
                temperature = float(terms[1])
                terms = terms[2:]
            except:
                raise RuntimeError('Invalid run_dislocation command: temperature')
        else:
            raise RuntimeError('Invalid run_dislocation command')
    
    i_potential = []
    i_crystal = []    
    i_phase = []
    i_disl = []
    struct_dir = os.path.join(ipr_dir, 'results', 'json', 'struct')
    
    for potential in potentials:
        for crystal in crystals:
            json_name = 'struct--' + potential.get('id') + '--' + crystal['proto'].get('tag') + '-'
            for element in crystal['elements']:
                json_name += '-' + element
            json_name += '.json'
            
            try:
                phase = iprp.models.CrystalPhase(os.path.join(struct_dir, json_name))
            except:
                print 'Could not find ' + json_name
                continue
            
            #See if point defect corresponds to crystal prototype
            for disl in disls:
                if disl['proto'] == crystal['proto'].get('tag'):
                    i_potential.append(potential)
                    i_crystal.append(crystal)
                    i_phase.append(phase)
                    i_disl.append(disl)
                    
    nsims = len(i_phase)
    i_lammps_exe = [lammps_exe  for i in xrange(nsims)]
    i_ipr_dir =    [ipr_dir     for i in xrange(nsims)]
    i_size =       [size        for i in xrange(nsims)]
    i_temperature =[temperature for i in xrange(nsims)]
    i_xwidth =     [xwidth      for i in xrange(nsims)]
    i_ywidth =     [ywidth      for i in xrange(nsims)]
    
    mappit(iter_dislocation, i_lammps_exe, i_ipr_dir, i_potential, i_crystal, i_phase, i_disl, i_size, i_temperature, i_xwidth, i_ywidth)

#Isolated calculation packet
def iter_dislocation(lammps_exe, ipr_dir, potential, crystal, phase, disl, system_size, temperature, xwidth, ywidth):
    #Crystal properties
    proto = crystal['proto']
    elements = crystal['elements']
    masses = potential.masses(elements)
    ucell = proto.get('ucell')
    
    #Potential-specific properties
    alat = phase.get('alat')
    cij = phase.get('cij')
    units = potential.get('units')
    atom_style = potential.get('atom_style')
    
    #Dislocation properties
    disl_data = disl['data']
    disl_tag = disl['tag']
    axes = disl_data.get(disl_tag, 'axes')
    shift = disl_data.get(disl_tag, 'shift')
    burgers = alat * disl_data.get(disl_tag, 'burgers')
    cutoff = alat[0] * disl_data.get('Nye_cutoff')
    tmax = disl_data.get('Nye_angle')
    zwidth = alat[2] * disl_data.get(disl_tag, 'zwidth')
    p = []
    for pset in disl_data.get('Nye_p'):
        p.append(alat * pset)   
    
    #System properties
    pbc = [False, False, True]
    b_width = 3 * alat[0]
    plot_range = np.array([ xwidth, ywidth, zwidth ])
    
    T, ax_mag = ax_check(axes)
    
    #Create simulation output directory
    output_dir = os.path.join(ipr_dir, 'results', 'sim', potential.get('id'), 'disl') 
    try:
        os.chdir(output_dir)
    except:
        os.makedirs(output_dir)
    
    #Create and move to temporary directory
    temp_dir = tempfile.mkdtemp(dir=os.path.join(ipr_dir,'results','temp'))
    os.chdir(temp_dir) 

    #Set system size parameters
    s = np.zeros(3, dtype=np.int)
    for i in xrange(3):
        scale = ceil(system_size[i] / ax_mag[i])
        if scale % 2 == 1:
            scale += 1
        s[i] = scale / 2
    size = np.array( [[-s[0], s[0]], [-s[1], s[1]], [-s[2], s[2]]], dtype=np.int )

    #Specify file name information
    outfile = proto.get('tag') + '-' 
    for element in elements:
        outfile += '-' + element
    outfile += '--' + disl_tag 

    #Build dislocation-free system, sys0
    base_file = outfile + '--base.dump'
    atomtypes = []
    for i in xrange(len(elements)):
        atomtypes.append(iprp.AtomType(elements[i],masses[i]))
    sys0 = lmp.create_sys(lammps_exe, atomtypes, pbc, alat=alat, ucell=ucell, axes=axes, shift=shift, size=size)
    
    #Calculate nearest neighbor list (used by dd)
    sys0.neighbors(cutoff)
    
    #Transform Burgers vector and elastic constant matrix
    b = T.dot(burgers)
    C = c_transform( c_mn_to_c_ijkl(cij), T)

    #Run Stroh calculations
    strohdata = stroh_setup(C)
    pre_ln = stroh_preln(b, strohdata)
    for atom in sys0.atoms:
        disp = stroh_disp_point(atom.get('x'), atom.get('y'), b, strohdata)
        atom.set('Stroh_disp_x', disp[0])
        atom.set('Stroh_disp_y', disp[1])
        atom.set('Stroh_disp_z', disp[2])
        
        stress = stroh_stress_point(atom.get('x'), atom.get('y'), b, C, strohdata)
        atom.set('Stroh_stress_xx', stress[0,0])
        atom.set('Stroh_stress_xy', stress[0,1])
        atom.set('Stroh_stress_xz', stress[0,2])
        atom.set('Stroh_stress_yx', stress[1,0])
        atom.set('Stroh_stress_yy', stress[1,1])
        atom.set('Stroh_stress_yz', stress[1,2])
        atom.set('Stroh_stress_zx', stress[2,0])
        atom.set('Stroh_stress_zy', stress[2,1])
        atom.set('Stroh_stress_zz', stress[2,2])
    
    #Save base file
    lmp.write_dump( os.path.join(output_dir, base_file), sys0)
    
    #Displace atoms in system according to Stroh solution
    sys1 = deepcopy(sys0)
    strohdata = stroh_setup(C)
    for batom, datom in zip(sys0.atoms, sys1.atoms):
        disp = stroh_disp_point(batom.get('x'), batom.get('y'), b, strohdata)
        newpos = batom.get('pos') + disp
        if newpos[2] < sys1.box[2,0]:
            newpos[2] += (sys1.box[2,1] - sys1.box[2,0])
        elif newpos[2] > sys1.box[2,1]:
            newpos[2] -= (sys1.box[2,1] - sys1.box[2,0])
        datom.set('pos', newpos)
        
    #Apply boundary conditions
    sys1 = boundaryfix(sys1, b_width, 'circle')
    
    #Relax system
    pair_info = potential.coeff(sys1.elements())
    masses = sys1.masses()
    lmp.write_atom('disl.dat', sys1)
    
    with open('disl_relax.in', 'w') as f:
        f.write(disl_relax_script(pair_info, units, atom_style, masses, 'disl.dat', temp=temperature))

    disl_file = outfile + '--disl.dump'
    data = iprp.lammps.extract(subprocess.check_output(lammps_exe + ' < disl_relax.in',shell=True))
    sys2 = lmp.read_dump('atom.'+data[-1][0], atomtypes)
    sys2.set('axes', axes)
    
    #Calculate nearest neighbor list
    sys2.neighbors(cutoff)

    #Calculate the Nye tensor and save dump file
    nye(sys2, p, tmax)
    lmp.write_dump( os.path.join(output_dir, disl_file), sys2)
    
    #Clear and delete temporary directory
    os.chdir(output_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    #Create plots
    try:
        os.chdir(outfile)
    except:
        os.mkdir(outfile)
        os.chdir(outfile)
        
    #Plot dd
    if disl_tag == '(a-2)[(1)(1)(1)]--((-1)(0)(1))--u[(1)(1)(1)]' and proto.get('tag') == 'bcc':
        scale = [1.8856]
    else:
        scale = [1]        
    dd(sys0, sys2, plot_range, b, scale=scale, save=True, show=False)
    
    #Plot Nye data
    bx, avsum = a2cplot(sys2, 'nye_zx', plot_range, save=True, show=False)
    by, avsum = a2cplot(sys2, 'nye_zy', plot_range, save=True, show=False)
    bz, avsum = a2cplot(sys2, 'nye_zz', plot_range, save=True, show=False)
    
    json_file = 'disl--' + potential.get('id') + '--' + outfile + '.json'
    json_dir = os.path.join(ipr_dir,'results','json','disl')
    
    json_data = OrderedDict()
    json_data['calculationDislocationMonopole'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = potential.get('id')
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = proto.get('tag')
    
    #Add defect name
    sim['dislocationMonopoleID'] = OrderedDict()
    sim['dislocationMonopoleID']['dislocationTag'] = disl_tag
    
    #Add pre-ln energy factor
    sim['pre-lnEnergyFactor'] = OrderedDict([( 'value', pre_ln),
                                              ( 'unit',  'eV')       ])
    
    #Add Nye tensor estimate of the Burgers vector
    b_est = [float('%.3f' % bx), float('%.3f' % by), float('%.3f' % bz)]
    sim['nyeBurgersEstimate'] = b_est                                   

    with open(os.path.join(json_dir, json_file), 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))

    













    
if __name__ == '__main__':
    main(sys.argv)