#!/usr/bin/env python
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

from DataModelDict import DataModelDict

import sys
import random
import matplotlib.pyplot as plt
import numpy as np
import uuid
from copy import deepcopy

def read_input(fname):    
    """Interpret input file into DataModelDict"""
    with open(fname) as f:
        input_dict = DataModelDict()
        for line in f:
            terms = line.split()
            if len(terms) != 0 and terms[0][0] != '#':
                if len(terms) == 1:
                    input_dict[terms[0]] = None
                else:
                    for i in xrange(1, len(terms)):
                        input_dict.append(terms[0], terms[i])
                
    return input_dict

def alat_script(system_info, pair_info, delta = 1e-5, steps = 2):
    """
    Create a LAMMPS script that applies a hydrostatic strain.
    
    Keyword Arguments:
    system_info -- string containing LAMMPS commands for creating/reading a system.
    pair_info -- string containing LAMMPS commands specific to the interatomic potential.
    delta -- float value indicating strain range. Default is 1e-5.
    steps -- integer number of strain steps. Defaut is 2.    
    """
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
    """Create lammps script that strains a crystal in each direction x,y,z and shear yz,xz,xy independently."""    
        
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
        
def ecoh_vs_r(lammps_exe, ucell, potential, symbols, rmin=2.0, rmax=5.0, rsteps=200):
    """Measure cohesive energy of a crystal as a function of nearest neighbor distance, r0"""
    
    #Initial size setup
    r_a = r_a_ratio(ucell)
    amin = rmin / r_a
    amax = rmax / r_a
    alat0 = (amax + amin) / 2.
    delta = (amax-amin)/alat0
    
    #Create unit cell with a = alat0
    ucell.box_set(a = alat0, b = alat0 * ucell.box.b / ucell.box.a, c = alat0 * ucell.box.c / ucell.box.a, scale=True)

    #LAMMPS script setup
    pair_info = potential.pair_info(symbols)
    
    system_info = lmp.sys_gen(units =       potential.units,
                              atom_style =  potential.atom_style,
                              ucell =       ucell,
                              size =        np.array([[0,3], [0,3], [0,3]], dtype=np.int))

    #Write the LAMMPS input file
    with open('alat.in','w') as script:
        script.write(alat_script(system_info, pair_info, delta=delta, steps=rsteps))
    
    #Run LAMMPS
    data = lmp.run(lammps_exe, 'alat.in')
 
    #extract thermo data from log output 
    avalues = np.array(data.finds('Lx')) / 3.
    rvalues = avalues * r_a
    evalues = np.array(data.finds('peatom'))  
        
    #Use potential units and atom_style terms to convert values to appropriate length and energy units
    lmp_units = lmp.style.unit(potential.units)
    avalues = uc.set_in_units(avalues, lmp_units['length'])
    rvalues = uc.set_in_units(rvalues, lmp_units['length'])
    evalues = uc.set_in_units(evalues, lmp_units['energy'])
        
    return rvalues, avalues, evalues    

def r_a_ratio(ucell):
    """Calculates the shortest interatomic spacing, r, for a system wrt to box.a."""
    r_a = ucell.box.a
    for i in xrange(ucell.natoms):
        for j in xrange(i):
            dmag = np.linalg.norm(ucell.dvect(i,j))
            if dmag < r_a:
                r_a = dmag
    return r_a/ucell.box.a

def quick_a_Cij(lammps_exe, ucell, potential, symbols, p_xx=0.0, p_yy=0.0, p_zz=0.0, tol=1e-10, diverge_scale=3.):
    """
    Quickly refines static orthorhombic cell by evaluating the elastic constants and the virial pressure.
    
    Keyword Arguments:
    lammps_exe -- directory location for lammps executable
    system -- atomman.System to statically deform and evaluate a,b,c and Cij at a given pressure
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    pxx, pyy, pzz -- tensile pressures to equilibriate to.  Default is 0.0 for all.  
    tol -- the relative tolerance criterion for identifying box size convergence. Default is 1e-10.
    diverge_scale -- identifies a divergent system if x / diverge_scale < x < x * diverge_scale is not True for x = a,b,c.
    """
    
    #initial parameter setup
    converged = False                   #flag for if values have converged
    
    #define boxes for iterating
    ucell_current = deepcopy(ucell)     #ucell with box parameters being evaluated
    ucell_old = None                    #ucell with previous box parameters evaluated
    
    for cycle in xrange(100):
        
        #Run LAMMPS and evaluate results based on ucell_old
        results = calc_cij(lammps_exe, ucell_current, potential, symbols, p_xx, p_yy, p_zz)
        ucell_new = results['ucell_new']
        
        #Test if box has converged to a single size
        if np.allclose(ucell_new.box.vects, ucell_current.box.vects, rtol=tol):
            converged = True
            break
        
        #Test if box has converged to two sizes
        elif ucell_old is not None and np.allclose(ucell_new.box.vects, ucell_old.box.vects, rtol=tol):
            #Run LAMMPS Cij script using average between alat0 and alat1
            box = am.Box(a = (ucell_new.box.a + ucell_old.box.a) / 2.,
                         b = (ucell_new.box.b + ucell_old.box.b) / 2.,
                         c = (ucell_new.box.c + ucell_old.box.c) / 2.)
            ucell_current.box_set(vects=box.vects, scale=True)
            results = calc_cij(lammps_exe, ucell_current, potential, symbols, p_xx, p_yy, p_zz)                 
            
            converged = True
            break
        
        #Test if values have diverged from initial guess
        elif ucell_new.box.a < ucell.box.a / diverge_scale or ucell_new.box.a > ucell.box.a * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif ucell_new.box.b < ucell.box.b / diverge_scale or ucell_new.box.b > ucell.box.b * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif ucell_new.box.c < ucell.box.c / diverge_scale or ucell_new.box.c > ucell.box.c * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')  
        elif results['ecoh'] == 0.0:
            raise RuntimeError('Divergence: cohesive energy is 0')
                
        #if not converged or diverged, update ucell_old and ucell_current
        else:
            ucell_old, ucell_current = ucell_current, ucell_new
    
    #Return values if converged
    if converged:        
        return results
    else:
        raise RuntimeError('Failed to converge after 100 cycles')

def calc_cij(lammps_exe, ucell, potential, symbols, p_xx=0.0, p_yy=0.0, p_zz=0.0):
    """Runs cij_script and returns current Cij, stress, Ecoh, and new ucell guess."""
    
    #setup system and pair info
    system_info = lmp.sys_gen(units =       potential.units,
                              atom_style =  potential.atom_style,
                              ucell =       ucell,
                              size =        np.array([[0,3], [0,3], [0,3]]))

    pair_info = potential.pair_info(symbols)
    
    #create script and run
    with open('cij.in','w') as f:
        f.write(cij_script(system_info, pair_info))
    data = lmp.run(lammps_exe, 'cij.in')
    
    #get units for pressure and energy used by LAMMPS simulation
    lmp_units = lmp.style.unit(potential.units)
    p_unit = lmp_units['pressure']
    e_unit = lmp_units['energy']
    
    #Extract thermo values. Each term ranges i=0-12 where i=0 is undeformed
    #The remaining values are for -/+ strain pairs in the six unique directions
    lx = np.array(data.finds('Lx'))
    ly = np.array(data.finds('Ly'))
    lz = np.array(data.finds('Lz'))
    xy = np.array(data.finds('Xy'))
    xz = np.array(data.finds('Xz'))
    yz = np.array(data.finds('Yz'))
    
    pxx = uc.set_in_units(np.array(data.finds('Pxx')), p_unit)
    pyy = uc.set_in_units(np.array(data.finds('Pyy')), p_unit)
    pzz = uc.set_in_units(np.array(data.finds('Pzz')), p_unit)
    pxy = uc.set_in_units(np.array(data.finds('Pxy')), p_unit)
    pxz = uc.set_in_units(np.array(data.finds('Pxz')), p_unit)
    pyz = uc.set_in_units(np.array(data.finds('Pyz')), p_unit)
    
    pe = uc.set_in_units(np.array(data.finds('peatom')), e_unit)
    
    #Set the six non-zero strain values
    strains = np.array([ (lx[2] -  lx[1])  / lx[0],
                         (ly[4] -  ly[3])  / ly[0],
                         (lz[6] -  lz[5])  / lz[0],
                         (yz[8] -  yz[7])  / lz[0],
                         (xz[10] - xz[9])  / lz[0],
                         (xy[12] - xy[11]) / ly[0] ])

    #calculate cij using stress changes associated with each non-zero strain
    cij = np.empty((6,6))
    for i in xrange(6):
        delta_stress = np.array([ pxx[2*i+1]-pxx[2*i+2],
                                  pyy[2*i+1]-pyy[2*i+2],
                                  pzz[2*i+1]-pzz[2*i+2],
                                  pyz[2*i+1]-pyz[2*i+2],
                                  pxz[2*i+1]-pxz[2*i+2],
                                  pxy[2*i+1]-pxy[2*i+2] ])

        cij[i] = delta_stress / strains[i] 
        
    for i in xrange(6):
        for j in xrange(i):
            cij[i,j] = cij[j,i] = (cij[i,j] + cij[j,i]) / 2

    C = am.tools.ElasticConstants(Cij=cij)
    
    if np.allclose(C.Cij, 0.0):
        raise RuntimeError('Divergence of elastic constants to <= 0')
    try:
        S = C.Sij
    except:
        raise RuntimeError('singular C:\n'+str(C.Cij))

    
    #extract the current stress state
    stress = -1 * np.array([[pxx[0], pxy[0], pxz[0]],
                            [pxy[0], pyy[0], pyz[0]],
                            [pxz[0], pyz[0], pzz[0]]])
    
    s_xx = stress[0,0] + p_xx
    s_yy = stress[1,1] + p_yy
    s_zz = stress[2,2] + p_zz
    
    new_a = ucell.box.a / (S[0,0]*s_xx + S[0,1]*s_yy + S[0,2]*s_zz + 1)
    new_b = ucell.box.b / (S[1,0]*s_xx + S[1,1]*s_yy + S[1,2]*s_zz + 1)
    new_c = ucell.box.c / (S[2,0]*s_xx + S[2,1]*s_yy + S[2,2]*s_zz + 1)
    
    if new_a <= 0 or new_b <= 0 or new_c <=0:
        raise RuntimeError('Divergence of box dimensions to <= 0')
    
    newbox = am.Box(a=new_a, b=new_b, c=new_c)
    ucell_new = deepcopy(ucell)
    ucell_new.box_set(vects=newbox.vects, scale=True)
    
    return {'C':C, 'stress':stress, 'ecoh':pe[0], 'ucell_new':ucell_new}
    
def main(args):    
    """Main function for running calc_struct_static.py"""

    try:
        infile = args[0]
        try:
            UUID = args[1]
        except:
            UUID = str(uuid.uuid4())
    except:
        raise ValueError('Input file not given')

    #Read in parameters from input file
    input_dict = read_input(infile)

    #Initial parameter setup
    lammps_exe =   input_dict.get('lammps_exe')
    pot_dir =      input_dict.get('potential_dir', '')
    
    symbols =      input_dict.get('symbols') 
    
    u_length =     input_dict.get('length_display_units',   'angstrom')
    u_press =      input_dict.get('pressure_display_units', 'GPa')
    u_energy =     input_dict.get('energy_display_units',   'eV')
    r_min =        input_dict.get('r_min', None)
    r_max =        input_dict.get('r_max', None)
    
    if r_min is None:
        r_min = uc.get_in_units(2.0, 'angstrom')
    else:
        r_min = uc.get_in_units(float(r_min), u_length)
    if r_max is None:
        r_max = uc.get_in_units(5.0, 'angstrom')
    else:
        r_max = uc.get_in_units(float(r_max), u_length)
    steps = int(input_dict.get('steps', 200))

    #read in potential_file
    with open(input_dict['potential_file']) as f:
        potential = lmp.Potential(f, pot_dir)        
        
    #read in prototype_file
    with open(input_dict['crystal_file']) as f:
        ucell = am.System()
        try:
            ucell.load('system_model', f)
        except:
            f.seek(0)
            ucell.load('cif', f)
    
    #Run ecoh_vs_r
    rvals, avals, evals = ecoh_vs_r(lammps_exe, deepcopy(ucell), potential, symbols, rmin=r_min, rmax=r_max, rsteps=steps)
    
    #Use plot to get rough lattice parameter guess, a0, and build ucell
    a0 = avals[np.argmin(evals)]
    cell_0 = ucell.model(symbols=symbols, box_unit='scaled')

    ucell.box_set(a = a0, b = a0 * ucell.box.b / ucell.box.a, c = a0 * ucell.box.c / ucell.box.a, scale=True)

    #Run quick_aCij to refine values
    results = quick_a_Cij(lammps_exe, ucell, potential, symbols)
    
    #Plot Ecoh vs. r
    plt.title('Cohesive Energy vs. Interatomic Spacing')
    plt.xlabel('r (' + u_length + ')')
    plt.ylabel('Cohesive Energy (' + u_energy + '/atom)')
    plt.plot(uc.get_in_units(rvals, u_length), uc.get_in_units(evals, u_energy))
    plt.savefig('Ecoh_vs_r.png')
    plt.close()

    ucell_new = results['ucell_new']
    cell_1 = ucell_new.model(symbols=symbols, box_unit=u_length)
    ecoh = uc.get_in_units(results['ecoh'], u_energy)
    C = results['C']    
    
    output = DataModelDict()
    output['calculation-crystal-phase'] = calc = DataModelDict()
    calc['calculation-id'] = UUID
    
    with open(input_dict['potential_file']) as f:
        potdict = DataModelDict(f) 
    calc['potential'] = potdict['LAMMPS-potential']['potential']
    
    calc['crystal-info'] = DataModelDict()
    calc['crystal-info']['artifact'] = input_dict['crystal_file']
    calc['crystal-info']['symbols'] = symbols
    
    calc['phase-state'] = DataModelDict()
    calc['phase-state']['temperature'] = DataModelDict([('value', 0.0), ('unit', 'K')])
    calc['phase-state']['pressure'] = DataModelDict([('value', 0.0), ('unit', u_press)])
    
    calc['as-constructed-atomic-system'] = cell_0['atomic-system']
    
    calc['relaxed-atomic-system'] = cell_1['atomic-system']
    c_family = cell_1['atomic-system']['cell'].keys()[0]
    
    calc['cohesive-energy'] = DataModelDict([('value', ecoh), ('unit', u_energy)])
    calc['elastic-constants'] = C.model(unit=u_press, crystal_system=c_family)['elastic-constants']

    calc['cohesive-energy-relation'] = DataModelDict()
    calc['cohesive-energy-relation']['r'] = DataModelDict([('value', list(uc.get_in_units(rvals, u_length))), ('unit', u_length)])
    calc['cohesive-energy-relation']['a'] = DataModelDict([('value', list(uc.get_in_units(avals, u_length))), ('unit', u_length)])
    calc['cohesive-energy-relation']['cohesive-energy'] = DataModelDict([('value', list(uc.get_in_units(evals, u_length))), ('unit', u_energy)])
    
    with open('results.json', 'w') as f:
        output.json(fp=f, indent=4)
    
if __name__ == '__main__':
    main(sys.argv[1:])    

    
    
    
    
    
    
    
    
    