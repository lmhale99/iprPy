#!/usr/bin/env python2.7

# Standard library imports
import os
import subprocess
from multiprocessing import Pool
from copy import deepcopy
import sys
import tempfile

#Additional imports
import numpy as np

#Custom imports
import atomman as am


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
    
def ecoh_vs_r(lammps_exe, prototype, potential, symbols, rmin=2.0, rmax=5.0, rsteps=200):
    #Measure cohesive energy of a crystal prototype as a function of nearest neighbor distance, r0
    
    #Initial size setup
    r_a = prototype.r_a()
    amin = rmin / r_a
    amax = rmax / r_a
    alat0 = (amax + amin) / 2.
    delta = (amax-amin)/alat0
    
    ucell = prototype.ucell(alat0)

    #LAMMPS script setup
    pair_info = potential.pair_info(symbols)
    
    system_info = am.lammps.sys_gen(units =       potential.units(),
                                    atom_style =  potential.atom_style(),
                                    ucell_box =   ucell.box(),
                                    ucell_atoms = ucell.atoms(scale=True),
                                    size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))

    #Write the LAMMPS input file
    with open('alat.in','w') as script:
        script.write(alat_script(system_info, pair_info, delta=delta, steps=rsteps))
    
    #Run LAMMPS
    data = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in alat.in', shell=True))
 
    avalues = np.zeros((rsteps))
    evalues = np.zeros((rsteps))
    rvalues = np.zeros((rsteps))
    for c in xrange(rsteps):
        avalues[c] = np.float(data[c+1][1]) / 3.
        rvalues[c] = np.float(data[c+1][1]) / 3. * r_a
        evalues[c] = np.float(data[c+1][7])
        
    return rvalues, avalues, evalues    

def quick_lattice_refine(lammps_exe, ucell, potential, symbols):
    #Quickly computes static lattice parameters and elastic constants
    
    #initial parameter setup
    converged = False                   #flag for if values have converged
    dimensions = np.empty((13,6))       #system dimensions taken from simulation results
    stresses = np.empty((13,6))         #system virial stresses (-pressures) taken from sim results
    
    #needed parameters from the potential
    pair_info = potential.pair_info(symbols)

    #define boxes for iterating
    box_init = deepcopy(ucell.box())    #box of original parameters
    box0 = deepcopy(ucell.box())        #box of parameters being evaluated
    box1 = am.Box()                     #box of new parameters based on analysis
    boxn1 = am.Box()                    #box of parameters from prior to alat0
    
    for cycle in xrange(100):
        #Run LAMMPS Cij script using guess alat0
        
        system_info = am.lammps.sys_gen(units =       potential.units(),
                                        atom_style =  potential.atom_style(),
                                        ucell_box =   box0,
                                        ucell_atoms = ucell.atoms(scale=True),
                                        size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))
        
        f = open('cij.in','w')
        f.write(cij_script(system_info, pair_info))
        f.close()
        data = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in cij.in', shell=True))
        
        #Extract system dimensions and stresses from LAMMPS data output
        for p in xrange(13):
            for i in xrange(6):
                dimensions[p, i] = float(data[p+1][i+1])
                stresses[p, i] = -float(data[p+1][i+7]) * 1e-4
        eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                              dimensions[0,2], dimensions[0,2], dimensions[0,1]])

        #Calculate Cij from dimensions and pressures
        cij = np.empty((6,6))
        for i in xrange(0,6):
            eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]
            for j in xrange(0,6):
                sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                cij[j,i] = sig_ij/eps_ij
        
        #Invert Cij to Sij and compute new box1
        S = np.linalg.inv(cij)
        box1 = am.Box(a=(dimensions[0,0] / (S[0,0]*stresses[0,0] + S[0,1]*stresses[0,1] + S[0,2]*stresses[0,2] + 1)) / 3.,
                      b=(dimensions[0,1] / (S[1,0]*stresses[0,0] + S[1,1]*stresses[0,1] + S[1,2]*stresses[0,2] + 1)) / 3.,
                      c=(dimensions[0,2] / (S[2,0]*stresses[0,0] + S[2,1]*stresses[0,1] + S[2,2]*stresses[0,2] + 1)) / 3.)
        
        #Test if values have converged to one value
        if (np.isclose(box0.get('a'), box1.get('a'), rtol=0, atol=1e-13) and
            np.isclose(box0.get('b'), box1.get('b'), rtol=0, atol=1e-13) and
            np.isclose(box0.get('c'), box1.get('c'), rtol=0, atol=1e-13)):
            converged = True
            break
            
        #Test if values have diverged from initial guess
        elif (box1.get('a') < box_init.get('a') / 5. or box1.get('a') > box_init.get('a') * 5. or
              box1.get('b') < box_init.get('b') / 5. or box1.get('b') > box_init.get('b') * 5. or
              box1.get('c') < box_init.get('c') / 5. or box1.get('c') > box_init.get('c') * 5.):
            break
            
        #Test if values have converged to two values 
        elif (np.isclose(boxn1.get('a'), box1.get('a'), rtol=0, atol=1e-13) and
              np.isclose(boxn1.get('b'), box1.get('b'), rtol=0, atol=1e-13) and
              np.isclose(boxn1.get('c'), box1.get('c'), rtol=0, atol=1e-13)):
            
            #Run LAMMPS Cij script using average between alat0 and alat1
            box0 = am.Box(a = (box1.get('a') + box0.get('a')) / 2.,
                          b = (box1.get('b') + box0.get('b')) / 2.,
                          c = (box1.get('c') + box0.get('c')) / 2.)
                             
            system_info = am.lammps.sys_gen(units =       potential.units(),
                                            atom_style =  potential.atom_style(),
                                            ucell_box =   box0,
                                            ucell_atoms = ucell.atoms(scale=True),
                                            size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))
        
            f = open('cij.in','w')
            f.write(cij_script(system_info, pair_info))
            f.close()
            data = am.lammps.log_extract(subprocess.check_output(lammps_exe+' -in cij.in',shell=True))
            
            #Extract system dimensions and pressures from LAMMPS data output
            for p in xrange(13):
                for i in xrange(6):
                    dimensions[p, i] = float(data[p+1][i+1])
                    stresses[p, i] = -float(data[p+1][i+10])*1e-4
            eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                                  dimensions[0,2], dimensions[0,2], dimensions[0,1]])

            #Calculate Cij from LAMMPS results
            cij = np.empty((6,6))
            for i in xrange(0,6):
                eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]  
                for j in xrange(0,6):
                    sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                    cij[j,i] = sig_ij/eps_ij
            converged = True
            break
            
        #if not converged or diverged, shift box1 -> box0 -> boxn1
        else:
            boxn1 = deepcopy(box0)
            box0 =  deepcopy(box1)
    
    #Return values if converged
    if converged:        
        ecoh = float(data[1][13])
        return {'box':box0, 'ecoh':ecoh, 'cij':cij}
    else:
        return None     
    
def iterbox(a, b):
    #Allows for dynamic iteration over all arrays of length b where each term is in range 0-a
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j    
        elif b == 1:
            yield [i]     

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
                elif terms[0] == 'prototype_dir':
                    input_dict['prototype_dir'] = terms[1]
                elif terms[0] == 'r_min':
                    input_dict['r_min'] = float(terms[1])
                elif terms[0] == 'r_max':
                    input_dict['r_max'] = float(terms[1])
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
        test = input_dict['prototype_dir']
    except:
        input_dict['prototype_dir'] = os.getcwd()
    try:
        test = input_dict['r_min']
    except:
        input_dict['r_min'] = 2.0
    try:
        test = input_dict['r_max']
    except:
        input_dict['r_max'] = 5.0    
    try:
        test = input_dict['steps']
    except:
        input_dict['steps'] = 200  

    return input_dict

def iter_run(values):
    lammps_exe = values[0]
    prototype = values[1]
    potential = values[2]
    symbols = values[3]
    rmin = values[4]
    rmax = values[5]
    rsteps = values[6]
    
    starting_dir = os.getcwd()
    #Create and move to temporary directory    
    temp_dir = tempfile.mkdtemp(dir=starting_dir)
    os.chdir(temp_dir)
    
    #Create instance of Crystal Phase data model
    results = am.tools.CrystalPhase()
    results.define(potential, prototype, symbols)
    
    #Run e-vs-r0 calculations
    rvals, avals, evals = ecoh_vs_r(lammps_exe, prototype, potential, symbols, rmin, rmax, rsteps)
    results.set_E_vs_r_data(rvals, avals, evals)
   
    #Construct unit cell based on minimum ecoh
    ucell0 = prototype.ucell()
    mindex = np.argmin(evals)
    atest = avals[mindex]
    
    ucell = prototype.ucell(a = atest * ucell0.box('a'),
                            b = atest * ucell0.box('b'), 
                            c = atest * ucell0.box('c'), 
                            alpha = ucell0.box('alpha'),
                            beta  = ucell0.box('beta'), 
                            gamma = ucell0.box('gamma'))    
    
    adata = quick_lattice_refine(lammps_exe, ucell, potential, symbols)
    
    try:
        box = adata['box']
        alat = (box.get('a'), box.get('b'), box.get('c'))
        results.values('ecoh',  adata['ecoh'])
        results.values('alat',  alat)
        results.values('cij',   adata['cij'])    
    except:
        pass
    
    #Clear and delete temporary directory
    os.chdir(starting_dir)
    for fname in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    #Create json output file
    out_file = 'struct--' + str(potential) + '--' + prototype.get('tag') + '-'
    for symbol in symbols:
        out_file += '-' + potential.elements(symbol)   
    out_file += '.json'
    results.dump(out_file)
    
    
    
if __name__ == '__main__':
    
    #Read in parameters from input file
    input_dict = read_input(sys.argv[1])
    
    #Read interatomic potential file
    pot_file = input_dict['potential_file']
    pot_dir  = input_dict['potential_dir']
    potential = am.lammps.Potential(pot_file, pot_dir)
    all_symbols = potential.symbols()
    
    #Read in crystal prototypes
    proto_dir = input_dict['prototype_dir']
    prototypes = []
    flist = os.listdir(proto_dir)
    for fname in flist:
        try:  
            prototypes.append(am.tools.Prototype( os.path.join(proto_dir, fname) ))
        except:
            pass
    
    #iterate over all prototypes to build run parameters list
    lammps_exe = input_dict['lammps_exe']
    r_min = input_dict['r_min']
    r_max = input_dict['r_max']
    steps = input_dict['steps']
    run_values = []
    for prototype in prototypes:
        ucell = prototype.ucell()
        
        #iterate over all element-site combinations
        for el_array in iterbox(len(all_symbols), ucell.natypes()):
            
            #Build symbols list for the particular iteration
            symbols = []
            for el_index in el_array:
                symbols.append(all_symbols[el_index])
                
            run_values.append((lammps_exe, prototype, potential, symbols, r_min, r_max, steps))
    
    #Run serially (useful for debugging)
    if input_dict['np'] == 1:
        for i in xrange(len(run_values)):
            iter_run(run_values[i]) 
    #Run in parallel
    else:
        pool = Pool(input_dict['np'], maxtasksperchild=1)
        pool.map(iter_run, run_values)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    