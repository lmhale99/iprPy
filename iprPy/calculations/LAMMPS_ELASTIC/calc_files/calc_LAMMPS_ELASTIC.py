#!/usr/bin/env python
import os
import sys

import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

import iprPy

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):
    """Main function for running calculation"""
    
    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = iprPy.calculation_read_input(__calc_type__, f, *args[1:])
        
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
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
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
        
if __name__ == '__main__':
    main(*sys.argv[1:]) 