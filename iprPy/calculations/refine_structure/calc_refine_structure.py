#!/usr/bin/env python

#Standard library imports
import os
import sys
from copy import deepcopy
import uuid
import shutil

#http://www.numpy.org/
import numpy as np  

#https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

#https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):    
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])      
    
    #Run quick_a_Cij to refine values
    results_dict = quick_a_Cij(input_dict['lammps_command'], 
                               input_dict['initial_system'], 
                               input_dict['potential'],
                               input_dict['symbols'], 
                               p_xx = input_dict['pressure_xx'], 
                               p_yy = input_dict['pressure_yy'], 
                               p_zz = input_dict['pressure_zz'],
                               delta = input_dict['strain_range'])
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
        
def quick_a_Cij(lammps_command, system, potential, symbols, mpi_command=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, delta = 1e-5, tol=1e-10, diverge_scale=3.):
    """
    Quickly refines static orthorhombic system by evaluating the elastic constants and the virial pressure.
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to statically deform and evaluate a,b,c and Cij at a given pressure
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    
    Keyword Arguments:
    pxx, pyy, pzz -- tensile pressures to equilibriate to.  Default is 0.0 for all. 
    delta -- the strain range to use in calculating the elastic constants. Default is 1e-5.    
    tol -- the relative tolerance criterion for identifying box size convergence. Default is 1e-10.
    diverge_scale -- identifies a divergent system if x / diverge_scale < x < x * diverge_scale is not True for x = a,b,c.
    """
    
    #initial parameter setup
    converged = False                   #flag for if values have converged
    
    #define boxes for iterating
    system_current = deepcopy(system)       #system with box parameters being evaluated
    system_old = None                     #system with previous box parameters evaluated
    
    for cycle in xrange(100):
        
        #Run LAMMPS and evaluate results based on system_old
        results = calc_cij(lammps_command, system_current, potential, symbols, p_xx, p_yy, p_zz, delta, cycle)
        system_new = results['system_new']
        
        #Test if box has converged to a single size
        if np.allclose(system_new.box.vects, system_current.box.vects, rtol=tol):
            converged = True
            break
        
        #Test if box has converged to two sizes
        elif system_old is not None and np.allclose(system_new.box.vects, system_old.box.vects, rtol=tol):
            #Run LAMMPS Cij script using average between alat0 and alat1
            box = am.Box(a = (system_new.box.a + system_old.box.a) / 2.,
                         b = (system_new.box.b + system_old.box.b) / 2.,
                         c = (system_new.box.c + system_old.box.c) / 2.)
            system_current.box_set(vects=box.vects, scale=True)
            results = calc_cij(lammps_command, system_current, potential, symbols, p_xx, p_yy, p_zz, delta, cycle+1)                 
            
            converged = True
            break
        
        #Test if values have diverged from initial guess
        elif system_new.box.a < system.box.a / diverge_scale or system_new.box.a > system.box.a * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.b < system.box.b / diverge_scale or system_new.box.b > system.box.b * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.c < system.box.c / diverge_scale or system_new.box.c > system.box.c * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')  
        elif results['ecoh'] == 0.0:
            raise RuntimeError('Divergence: cohesive energy is 0')
                
        #if not converged or diverged, update system_old and system_current
        else:
            system_old, system_current = system_current, system_new
    
    #Return values if converged
    if converged:        
        return results
    else:
        raise RuntimeError('Failed to converge after 100 cycles')

def calc_cij(lammps_command, system, potential, symbols, p_xx=0.0, p_yy=0.0, p_zz=0.0, delta=1e-5, cycle=0):
    """Runs cij_script and returns current Cij, stress, Ecoh, and new system guess."""
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.sys_gen(units =       potential.units,
                                                          atom_style =  potential.atom_style,
                                                          ucell =       system,
                                                          size =        np.array([[0,3], [0,3], [0,3]]))
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['delta'] = delta
    lammps_variables['steps'] = 2
    
    #Write lammps input script
    template_file = 'cij.template'
    lammps_script = 'cij.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))
    
    #Run lammps 
    output = lmp.run(lammps_command, lammps_script)
    shutil.move('log.lammps', 'cij-'+str(cycle)+'-log.lammps')
    
    #Extract LAMMPS thermo data. Each term ranges i=0-12 where i=0 is undeformed
    #The remaining values are for -/+ strain pairs in the six unique directions
    lx = uc.set_in_units(np.array(output.finds('Lx')), lammps_units['length'])
    ly = uc.set_in_units(np.array(output.finds('Ly')), lammps_units['length'])
    lz = uc.set_in_units(np.array(output.finds('Lz')), lammps_units['length'])
    xy = uc.set_in_units(np.array(output.finds('Xy')), lammps_units['length'])
    xz = uc.set_in_units(np.array(output.finds('Xz')), lammps_units['length'])
    yz = uc.set_in_units(np.array(output.finds('Yz')), lammps_units['length'])
    
    pxx = uc.set_in_units(np.array(output.finds('Pxx')), lammps_units['pressure'])
    pyy = uc.set_in_units(np.array(output.finds('Pyy')), lammps_units['pressure'])
    pzz = uc.set_in_units(np.array(output.finds('Pzz')), lammps_units['pressure'])
    pxy = uc.set_in_units(np.array(output.finds('Pxy')), lammps_units['pressure'])
    pxz = uc.set_in_units(np.array(output.finds('Pxz')), lammps_units['pressure'])
    pyz = uc.set_in_units(np.array(output.finds('Pyz')), lammps_units['pressure'])
    
    pe = uc.set_in_units(np.array(output.finds('peatom')), lammps_units['energy'])
    
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

    C = am.ElasticConstants(Cij=cij)
    
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
    
    new_a = system.box.a / (S[0,0]*s_xx + S[0,1]*s_yy + S[0,2]*s_zz + 1)
    new_b = system.box.b / (S[1,0]*s_xx + S[1,1]*s_yy + S[1,2]*s_zz + 1)
    new_c = system.box.c / (S[2,0]*s_xx + S[2,1]*s_yy + S[2,2]*s_zz + 1)
    
    if new_a <= 0 or new_b <= 0 or new_c <=0:
        raise RuntimeError('Divergence of box dimensions to <= 0')
    
    newbox = am.Box(a=new_a, b=new_b, c=new_c)
    system_new = deepcopy(system)
    system_new.box_set(vects=newbox.vects, scale=True)
    
    return {'C':C, 'stress':stress, 'ecoh':pe[0], 'system_new':system_new}

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = iprPy.input.file_to_dict(f)
    
    #set calculation UUID
    if UUID is not None: input_dict['uuid'] = UUID
    else: input_dict['uuid'] = input_dict.get('uuid', str(uuid.uuid4()))
    
    #Process command lines
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    input_dict['mpi_command'] = input_dict.get('mpi_command', None)
    
    #Process potential
    iprPy.input.lammps_potential(input_dict)
    
    #Process default units
    iprPy.input.units(input_dict)
    
    #Process system information
    iprPy.input.system_load(input_dict)
    
    #Process system manipulations
    if input_dict['ucell'] is not None:
        iprPy.input.system_manipulate(input_dict)
    
    #Process run parameters
    #these are integer terms
    input_dict['number_of_steps_r'] = int(input_dict.get('number_of_steps_r', 200))
    
    #these are unitless float terms
    input_dict['strain_range'] = float(input_dict.get('strain_range', 1e-5))
    
    #these are terms with units
    input_dict['pressure_xx'] = iprPy.input.value_unit(input_dict, 'pressure_xx', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_yy'] = iprPy.input.value_unit(input_dict, 'pressure_yy', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_zz'] = iprPy.input.value_unit(input_dict, 'pressure_zz', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')    
    
    return input_dict
    
def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-system-relax'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['strain-range'] = input_dict['strain_range']
    run_params['load_options'] = input_dict['load_options']
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
    
    #Copy over potential data model info
    calc['potential'] = input_dict['potential_model']['LAMMPS-potential']['potential']
    
    #Save info on system file loaded
    system_load = input_dict['load'].split(' ')    
    calc['system-info'] = DM()
    calc['system-info']['artifact'] = DM()
    calc['system-info']['artifact']['file'] = os.path.basename(' '.join(system_load[1:]))
    calc['system-info']['artifact']['format'] = system_load[0]
    calc['system-info']['artifact']['family'] = input_dict['system_family']
    calc['system-info']['symbols'] = input_dict['symbols']
    
    #Save phase-state info
    calc['phase-state'] = DM()
    calc['phase-state']['temperature'] = DM([('value', 0.0), ('unit', 'K')])
    calc['phase-state']['pressure-xx'] = DM([('value', uc.get_in_units(input_dict['pressure_xx'],
                                                                       input_dict['pressure_unit'])), 
                                                       ('unit', input_dict['pressure_unit'])])
    calc['phase-state']['pressure-yy'] = DM([('value', uc.get_in_units(input_dict['pressure_yy'],
                                                                       input_dict['pressure_unit'])),
                                                       ('unit', input_dict['pressure_unit'])])
    calc['phase-state']['pressure-zz'] = DM([('value', uc.get_in_units(input_dict['pressure_zz'],
                                                                       input_dict['pressure_unit'])),
                                                       ('unit', input_dict['pressure_unit'])])                                                       
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        #Save data model of the initial ucell
        calc['as-constructed-atomic-system'] = input_dict['ucell'].model(symbols = input_dict['symbols'], 
                                                                         box_unit = input_dict['length_unit'])['atomic-system']
        
        #Update ucell to relaxed lattice parameters
        a_mult = input_dict['size_mults'][0][1] - input_dict['size_mults'][0][0]
        b_mult = input_dict['size_mults'][1][1] - input_dict['size_mults'][1][0]
        c_mult = input_dict['size_mults'][2][1] - input_dict['size_mults'][2][0]
        relaxed_ucell = deepcopy(input_dict['ucell'])
        relaxed_ucell.box_set(a = results_dict['system_new'].box.a / a_mult,
                              b = results_dict['system_new'].box.b / b_mult,
                              c = results_dict['system_new'].box.c / c_mult,
                              scale = True)
        
        #Save data model of the relaxed ucell                      
        calc['relaxed-atomic-system'] = relaxed_ucell.model(symbols = input_dict['symbols'], 
                                                            box_unit = input_dict['length_unit'])['atomic-system']
        
        #Save the final cohesive energy
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['ecoh'], 
                                                                           input_dict['energy_unit'])), 
                                                 ('unit', input_dict['energy_unit'])])
        
        #Save the final elastic constants
        c_family = calc['relaxed-atomic-system']['cell'].keys()[0]
        calc['elastic-constants'] = results_dict['C'].model(unit = input_dict['pressure_unit'], 
                                                            crystal_system = c_family)['elastic-constants']

    return output
    
if __name__ == '__main__':
    main(*sys.argv[1:])    