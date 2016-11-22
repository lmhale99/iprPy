#!/usr/bin/env python

#Standard library imports
import os
import sys
from copy import deepcopy
import uuid

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
        
    results_dict = lammps_ELASTIC(input_dict['lammps_command'], 
                                  input_dict['initial_system'],
                                  input_dict['potential'],
                                  input_dict['symbols'],
                                  mpi_command =   input_dict['mpi_command'],
                                  strain_range =  input_dict['strain_range'],
                                  etol =          input_dict['energy_tolerance'],
                                  ftol =          input_dict['force_tolerance'],
                                  maxiter =       input_dict['maximum_iterations'],
                                  maxeval =       input_dict['maximum_evaluations'],
                                  dmax =          input_dict['maximum_atomic_motion'],
                                  pressure_unit = input_dict['pressure_unit'])
                                  
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)        

def lammps_ELASTIC(lammps_command, system, potential, symbols, mpi_command=None, 
                   strain_range=1e-6, etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, 
                   dmax=0.01, pressure_unit='GPa'):

    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    #Define lammps variables
    lammps_variables = {}
    
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', units=potential.units, atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['strain_range'] = strain_range
    lammps_variables['pressure_unit_scaling'] = uc.get_in_units(uc.set_in_units(1.0, lammps_units['pressure']), pressure_unit)
    lammps_variables['pressure_unit'] = pressure_unit
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    #Fill in mod.template files
    with open('init.mod.template') as template_file:
        template = template_file.read()
    with open('init.mod', 'w') as in_file:
        in_file.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))
    with open('potential.mod.template') as template_file:
        template = template_file.read()
    with open('potential.mod', 'w') as in_file:
        in_file.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))    
    
    output = lmp.run(lammps_command, 'in.elastic', mpi_command)
    
    #Extract output values
    relaxed = output['LAMMPS-log-thermo-data']['simulation'][0]
    
    results = {}
    results['E_coh'] = uc.set_in_units(relaxed['thermo']['PotEng'][-1], lammps_units['energy']) / system.natoms
    results['lx'] =    uc.set_in_units(relaxed['thermo']['Lx'][-1],     lammps_units['length'])
    results['ly'] =    uc.set_in_units(relaxed['thermo']['Ly'][-1],     lammps_units['length'])
    results['lz'] =    uc.set_in_units(relaxed['thermo']['Lz'][-1],     lammps_units['length'])
    
    with open('log.lammps') as log_file:
        log = log_file.read()
    
    start = log.find('print "Elastic Constant C11all = ${C11all} ${cunits}"')
    lines = log[start+54:].split('\n')

    for line in lines:
        terms = line.split()
        if len(terms) > 0 and terms[0] == 'Elastic':
            c_term = terms[2][:3]
            c_value = terms[4]
            results['c_unit'] = terms[5]
            results[c_term] = c_value
                
    return results    

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
    input_dict['maximum_iterations'] =  int(input_dict.get('maximum_iterations',  100))
    input_dict['maximum_evaluations'] = int(input_dict.get('maximum_evaluations', 1000))
    
    #these are unitless floating point terms
    input_dict['strain_range'] =     float(input_dict.get('strain_range',     1e-6))
    input_dict['energy_tolerance'] = float(input_dict.get('energy_tolerance', 0.0))
    
    #these are terms with units
    input_dict['force_tolerance'] =       iprPy.input.value_unit(input_dict, 'force_tolerance',
                                                           default_unit=input_dict['force_unit'],  
                                                           default_term='1.0e-10 eV/angstrom')             
    input_dict['maximum_atomic_motion'] = iprPy.input.value_unit(input_dict, 'maximum_atomic_motion', 
                                                           default_unit=input_dict['length_unit'], 
                                                           default_term='0.01 angstrom')
    
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
    calc['phase-state']['pressure-xx'] = DM([('value', 0.0), ('unit', input_dict['pressure_unit']) ])
    calc['phase-state']['pressure-yy'] = DM([('value', 0.0), ('unit', input_dict['pressure_unit']) ])
    calc['phase-state']['pressure-zz'] = DM([('value', 0.0), ('unit', input_dict['pressure_unit']) ])                                                      
    
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
        relaxed_ucell.box_set(a = results_dict['lx'] / a_mult,
                              b = results_dict['ly'] / b_mult,
                              c = results_dict['lz'] / c_mult,
                              scale = True)
        
        #Save data model of the relaxed ucell                      
        calc['relaxed-atomic-system'] = relaxed_ucell.model(symbols = input_dict['symbols'], 
                                                            box_unit = input_dict['length_unit'])['atomic-system']
        
        #Save the final cohesive energy
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['E_coh'], 
                                                                           input_dict['energy_unit'])), 
                                                 ('unit', input_dict['energy_unit'])])
        
        #Save the final elastic constants
        c_family = 'triclinic'
        calc['elastic-constants'] = DM()
        
        for i in xrange(1, 7):
            for j in xrange(i, 7):
                c = DM()
                c['stiffness'] = DM([ ('value', results_dict['C'+str(i)+str(j)]), ('unit', results_dict['c_unit']) ])
                c['ij'] = str(i)+' '+str(j)
                calc['elastic-constants'].append('C', c)

    return output
    
if __name__ == '__main__':
    main(*sys.argv[1:]) 