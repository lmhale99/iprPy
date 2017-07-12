#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
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

# Define calc_style and record_style
calc_style = 'refine_structure'
record_style = 'calculation-system-relax'

def main(*args):
    """Main function for running calculation"""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
    
    # Run quick_a_Cij to refine values
    results_dict = quick_a_Cij(input_dict['lammps_command'], 
                               input_dict['initialsystem'], 
                               input_dict['potential'],
                               input_dict['symbols'], 
                               mpi_command = input_dict['mpi_command'],
                               ucell = input_dict['ucell'],
                               p_xx = input_dict['pressure_xx'], 
                               p_yy = input_dict['pressure_yy'], 
                               p_zz = input_dict['pressure_zz'],
                               delta = input_dict['strainrange'])
    
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
        
def quick_a_Cij(lammps_command, system, potential, symbols, mpi_command=None, ucell=None,
                p_xx=0.0, p_yy=0.0, p_zz=0.0, delta = 1e-5, tol=1e-10, diverge_scale=3.):
    """
    Quickly refines static orthorhombic system by evaluating the elastic constants and the virial pressure.
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to statically deform and evaluate a,b,c and Cij at a given pressure
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    
    Keyword Arguments:
    mpi_command -- MPI command for running LAMMPS in parallel. Default value 
                   is None (serial run).  
    ucell -- an atomman.System representing a fundamental unit cell of the 
             system. If not given, ucell will be taken as system.
    p_xx, p_yy, p_zz -- tensile pressures to equilibriate to.  Default is 0.0 for all. 
    delta -- the strain range to use in calculating the elastic constants. Default is 1e-5.    
    tol -- the relative tolerance criterion for identifying box size convergence. Default is 1e-10.
    diverge_scale -- identifies a divergent system if x / diverge_scale < x < x * diverge_scale is not True for x = a,b,c.
    """
    
    # Initial parameter setup
    converged = False                   # flag for if values have converged
    
    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_b = system.box.b / ucell.box.b
    lz_c = system.box.c / ucell.box.c
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
    
    # Define boxes for iterating
    system_current = deepcopy(system)       # system with box parameters being evaluated
    system_old = None                       # system with previous box parameters evaluated
    
    for cycle in xrange(100):
        
        # Run LAMMPS and evaluate results based on system_old
        results = calc_cij(lammps_command, system_current, potential, symbols, 
                           mpi_command=mpi_command, 
                           p_xx=p_xx, p_yy=p_yy, p_zz=p_zz, 
                           delta=delta, cycle=cycle)
        system_new = results['system_new']
        
        # Test if box has converged to a single size
        if np.allclose(system_new.box.vects, system_current.box.vects, rtol=tol, atol=0):
            converged = True
            break
        
        # Test if box has converged to two sizes
        elif system_old is not None and np.allclose(system_new.box.vects, system_old.box.vects, rtol=tol, atol=0):
            # Update current box to average of old and new lattice constants
            system_current.box_set(a = (system_new.box.a + system_old.box.a) / 2.,
                                   b = (system_new.box.b + system_old.box.b) / 2.,
                                   c = (system_new.box.c + system_old.box.c) / 2., 
                                   scale=True)
            results = calc_cij(lammps_command, system_current, potential, symbols, 
                               mpi_command=mpi_command, 
                               p_xx=p_xx, p_yy=p_yy, p_zz=p_zz, 
                               delta=delta, cycle=cycle+1)                 
            converged = True
            break
        
        # Test if values have diverged from initial guess
        elif system_new.box.a < system.box.a / diverge_scale or system_new.box.a > system.box.a * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.b < system.box.b / diverge_scale or system_new.box.b > system.box.b * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')
        elif system_new.box.c < system.box.c / diverge_scale or system_new.box.c > system.box.c * diverge_scale:
            raise RuntimeError('Divergence of box dimensions')  
        elif results['E_coh'] == 0.0:
            raise RuntimeError('Divergence: cohesive energy is 0')
                
        # If not converged or diverged, update system_old and system_current
        else:
            system_old, system_current = system_current, system_new
    
    # Return values when converged
    if converged:  
        # Extract final ucell parameters
        results['a_lat'] = system_new.box.a / lx_a
        results['b_lat'] = system_new.box.b / ly_b
        results['c_lat'] = system_new.box.c / lz_c
        results['alpha_lat'] = alpha
        results['beta_lat']  = beta
        results['gamma_lat'] = gamma    
        
        # Rename system_new to system_relaxed
        results['system_relaxed'] = results.pop('system_new')
        return results
    else:
        raise RuntimeError('Failed to converge after 100 cycles')

def calc_cij(lammps_command, system, potential, symbols, 
             mpi_command=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, delta=1e-5, cycle=0):
    """Runs cij_script and returns current Cij, stress, Ecoh, and new system guess."""
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init'+str(cycle)+'.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['delta'] = delta
    lammps_variables['steps'] = 2
    
    # Write lammps input script
    template_file = 'cij.template'
    lammps_script = 'cij.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, lammps_script, mpi_command=mpi_command, return_style='model')
    shutil.move('log.lammps', 'cij-'+str(cycle)+'-log.lammps')
    
    # Extract LAMMPS thermo data. Each term ranges i=0-12 where i=0 is undeformed
    # The remaining values are for -/+ strain pairs in the six unique directions
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
    try:
        pe = uc.set_in_units(np.array(output.finds('v_peatom')), lammps_units['energy'])
        assert len(pe) > 0
    except:
        pe = uc.set_in_units(np.array(output.finds('peatom')), lammps_units['energy'])
    
    # Set the six non-zero strain values
    strains = np.array([ (lx[2] -  lx[1])  / lx[0],
                         (ly[4] -  ly[3])  / ly[0],
                         (lz[6] -  lz[5])  / lz[0],
                         (yz[8] -  yz[7])  / lz[0],
                         (xz[10] - xz[9])  / lz[0],
                         (xy[12] - xy[11]) / ly[0] ])

    # Calculate cij using stress changes associated with each non-zero strain
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
    
    S = C.Sij
    
    # Extract the current stress state
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
    
    system_new = deepcopy(system)
    system_new.box_set(a=new_a, b=new_b, c=new_c, scale=True)
    
    return {'C_elastic':C, 'stress':stress, 'E_coh':pe[0], 'system_new':system_new}

def process_input(input_dict, UUID=None, build=True):
    """Reads the calc_*.in input commands for this calculation and sets default values if needed."""
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    input_dict['strainrange'] = float(input_dict.get('strainrange', 1e-6))
    input_dict['temperature'] = 0.0
    
    # These are calculation-specific default floats with units
    input_dict['pressure_xx'] = iprPy.input.value(input_dict, 'pressure_xx', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_yy'] = iprPy.input.value(input_dict, 'pressure_yy', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_zz'] = iprPy.input.value(input_dict, 'pressure_zz', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')    
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
if __name__ == '__main__':
    main(*sys.argv[1:])