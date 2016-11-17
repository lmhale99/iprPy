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
        input_dict = read_input(f, *args[1:])     
    
    results_dict = e_vs_r(input_dict['lammps_command'], 
                          input_dict['initial_system'], 
                          input_dict['potential'], 
                          input_dict['symbols'], 
                          mpi_command = input_dict['mpi_command'],
                          ucell = input_dict['ucell'],
                          rmin = input_dict['minimum_r'], 
                          rmax = input_dict['maximum_r'], 
                          rsteps = input_dict['number_of_steps_r'])
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
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
    
    #these are terms with units
    input_dict['minimum_r'] = iprPy.input.value_unit(input_dict, 'minimum_r', 
                                               default_unit=input_dict['length_unit'], 
                                               default_term='2.0 angstrom')
    input_dict['maximum_r'] = iprPy.input.value_unit(input_dict, 'maximum_r', 
                                               default_unit=input_dict['length_unit'], 
                                               default_term='6.0 angstrom')
    
    
    return input_dict

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-cohesive-energy-relation'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['size-multipliers'] = DM()

    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
    run_params['minimum_r'] = DM()
    run_params['minimum_r']['value'] = uc.get_in_units(input_dict['minimum_r'], input_dict['length_unit'])
    run_params['minimum_r']['unit'] = input_dict['length_unit']
    run_params['maximum_r'] = DM()
    run_params['maximum_r']['value'] = uc.get_in_units(input_dict['maximum_r'], input_dict['length_unit'])
    run_params['maximum_r']['unit'] = input_dict['length_unit']
    run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
    
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
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['cohesive-energy-relation'] = DM()
        calc['cohesive-energy-relation']['r'] = DM()
        calc['cohesive-energy-relation']['r']['value'] = list(uc.get_in_units(results_dict['r_values'], input_dict['length_unit']))
        calc['cohesive-energy-relation']['r']['unit'] = input_dict['length_unit']
        calc['cohesive-energy-relation']['a'] = DM()
        calc['cohesive-energy-relation']['a']['value'] = list(uc.get_in_units(results_dict['a_values'], input_dict['length_unit']))
        calc['cohesive-energy-relation']['a']['unit'] = input_dict['length_unit']
        calc['cohesive-energy-relation']['cohesive-energy'] = DM()
        calc['cohesive-energy-relation']['cohesive-energy']['value'] = list(uc.get_in_units(results_dict['Ecoh_values'], input_dict['energy_unit']))
        calc['cohesive-energy-relation']['cohesive-energy']['unit'] = input_dict['energy_unit']      

        if 'min_cell' in results_dict:
            for cell in results_dict['min_cell']:
                calc.append('minimum-atomic-system', cell.model(symbols = input_dict['symbols'], box_unit = input_dict['length_unit'])['atomic-system'])

    return output    
    
if __name__ == '__main__':
    main(*sys.argv[1:])    