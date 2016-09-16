#!/usr/bin/env python

#Standard library imports
import os
import sys
import random
from copy import deepcopy
import shutil

#http://www.numpy.org/
import numpy as np      

#https://github.com/usnistgov/atomman 
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

#Get calculation name and type
__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):    
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = iprPy.calculation_read_input(__calc_type__, f, *args[1:])
       
    #read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir'])        
    
    results_dict = e_vs_r(input_dict['lammps_command'], 
                          input_dict['initial_system'], 
                          potential, 
                          input_dict['symbols'], 
                          mpi_command = input_dict['mpi_command'],
                          ucell = input_dict['ucell'],
                          rmin = input_dict['minimum_r'], 
                          rmax = input_dict['maximum_r'], 
                          rsteps = input_dict['number_of_steps_r'])
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def e_vs_r(lammps_command, system, potential, symbols, mpi_command=None, ucell=None, rmin=2.0, rmax=6.0, rsteps=200):        
    """
    Performs a cohesive energy scan over a range of interatomic spaces, r.
    
    Arguments:
    lammps_command -- command for running LAMMPS.
    system -- atomman.System to perform the scan on.
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential.
    symbols -- list of element-model symbols for the Potential that 
               correspond to system's atypes.
    
    Keyword Arguments:
    
    mpi_command -- MPI command for running LAMMPS in parallel. Default value 
                   is None (serial run).  
    ucell -- an atomman.System representing a fundamental unit cell of the 
             system. If not given, ucell will be taken as system. 
    rmin -- the minimum r spacing to use. Default value is 2.0.
    rmax -- the minimum r spacing to use. Default value is 6.0.
    rsteps -- the number of r spacing steps to evaluate. Default value is 200.    
    """
    
    #Make system a deepcopy of itself (protect original from changes)
    system = deepcopy(system)
    
    #Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    #Calculate the r/a ratio for the unit cell
    r_a = r_a_ratio(ucell)
    
    #Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_a = system.box.b / ucell.box.a
    lz_a = system.box.c / ucell.box.a
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
 
    #build lists of values
    r_values = np.linspace(rmin, rmax, rsteps)
    a_values = r_values / r_a
    Ecoh_values = np.empty(rsteps)
 
    #Loop over values
    for i in xrange(rsteps):
        
        #Rescale system's box
        a = a_values[i]
        system.box_set(a = a * lx_a, 
                       b = a * ly_a, 
                       c = a * lz_a, 
                       alpha=alpha, beta=beta, gamma=gamma, scale=True)
        
        #Get lammps units
        lammps_units = lmp.style.unit(potential.units)
        
        #Define lammps variables
        lammps_variables = {}
        lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'atom.dat', units=potential.units, atom_style=potential.atom_style)
        lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
        
        #Write lammps input script
        template_file = 'run0.template'
        lammps_script = 'run0.in'
        with open(template_file) as f:
            template = f.read()
        with open(lammps_script, 'w') as f:
            f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))

        #Run lammps and extract data
        output = lmp.run(lammps_command, lammps_script, mpi_command)
        Ecoh_values[i] = uc.set_in_units(output.finds('peatom')[-1], lammps_units['energy'])
        shutil.move('log.lammps', 'run0-'+str(i)+'-log.lammps')
           
    #Find unit cell systems at the energy minimums
    min_cells = []
    for i in xrange(1, rsteps - 1):
        if Ecoh_values[i] < Ecoh_values[i-1] and Ecoh_values[i] < Ecoh_values[i+1]:
            a = a_values[i]
            cell = deepcopy(ucell)
            cell.box_set(a = a,
                         b = a * ucell.box.b / ucell.box.a,
                         c = a * ucell.box.c / ucell.box.a, 
                         alpha=alpha, beta=beta, gamma=gamma, scale=True)
            min_cells.append(cell)        
            
    return {'r_values':    r_values, 
            'a_values':    a_values, 
            'Ecoh_values': Ecoh_values, 
            'min_cell':    min_cells}
    
def r_a_ratio(ucell):
    """Calculates the shortest interatomic spacing, r, for a system wrt to box.a."""
    r_a = ucell.box.a
    for i in xrange(ucell.natoms):
        for j in xrange(i):
            dmag = np.linalg.norm(ucell.dvect(i,j))
            if dmag < r_a:
                r_a = dmag
    return r_a/ucell.box.a
    
if __name__ == '__main__':
    main(*sys.argv[1:])    