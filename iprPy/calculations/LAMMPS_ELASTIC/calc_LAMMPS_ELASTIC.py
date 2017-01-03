dzx#!/usr/bin/env python

#Standard library imports
import os
import sys
import uuid
import shutil
from copy import deepcopy

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
    
    interpret_input(input_dict)
    
    results_dict = lammps_ELASTIC_refine(input_dict['lammps_command'], 
                                         input_dict['initialsystem'],
                                         input_dict['potential'],
                                         input_dict['symbols'],
                                         mpi_command =   input_dict['mpi_command'],
                                         strainrange =   input_dict['strainrange'],
                                         etol =          input_dict['energytolerance'],
                                         ftol =          input_dict['forcetolerance'],
                                         maxiter =       input_dict['maxiterations'],
                                         maxeval =       input_dict['maxevaluations'],
                                         dmax =          input_dict['maxatommotion'],
                                         pressure_unit = input_dict['pressure_unit'])
                                  
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)        

def lammps_ELASTIC_refine(lammps_command, system, potential, symbols, mpi_command=None, 
                          strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, 
                          dmax=0.01, pressure_unit='GPa', tol=1e-10):
    """Repeatedly runs the ELASTIC example distributed with LAMMPS until box dimensions converge"""
    
    old_results = lammps_ELASTIC(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                                 strainrange=strainrange, etol=etol, ftol=ftol, 
                                 maxiter=maxiter, maxeval=maxeval, 
                                 dmax=dmax, pressure_unit=pressure_unit)
    shutil.move('log.lammps', 'elastic-0-log.lammps')
    
    converged = False
    for cycle in xrange(1, 100):
        new_results = lammps_ELASTIC(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                                     strainrange=strainrange, etol=etol, ftol=ftol, 
                                     maxiter=maxiter, maxeval=maxeval, 
                                     dmax=dmax, pressure_unit=pressure_unit)
        shutil.move('log.lammps', 'elastic-'+str(cycle)+'-log.lammps')
        
        #Test if box dimensions have converged
        if (np.isclose(old_results['lx'], new_results['lx'], rtol=tol, atol=0) and
            np.isclose(old_results['ly'], new_results['ly'], rtol=tol, atol=0) and
            np.isclose(old_results['lz'], new_results['lz'], rtol=tol, atol=0)):
            converged = True
            break
        else:
            old_results = new_results    
    
    #Return values if converged
    if converged:
        return new_results
    else:
        raise RuntimeError('Failed to converge after 100 cycles')
        
        
def lammps_ELASTIC(lammps_command, system, potential, symbols, mpi_command=None, 
                   strainrange=1e-6, etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, 
                   dmax=0.01, pressure_unit='GPa'):
    """Sets up and runs the ELASTIC example distributed with LAMMPS"""

    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)

    #Define lammps variables
    lammps_variables = {}
    
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', units=potential.units, atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['strainrange'] = strainrange
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
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    with open('potential.mod.template') as template_file:
        template = template_file.read()
    with open('potential.mod', 'w') as in_file:
        in_file.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))    
    
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
    input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    #set calculation UUID
    if UUID is not None: input_dict['calc_key'] = UUID
    else: input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    #Verify required terms are defined
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    assert 'potential_file' in input_dict, 'potential_file value not supplied'
    assert 'load'           in input_dict, 'load value not supplied'
    
    #Assign default values to undefined terms
    iprPy.input.units(input_dict)
    
    input_dict['mpi_command'] =    input_dict.get('mpi_command',    None)
    input_dict['potential_dir'] =  input_dict.get('potential_dir',  '')
    
    input_dict['load_options'] =   input_dict.get('load_options',   None)
    input_dict['box_parameters'] = input_dict.get('box_parameters', None)
    input_dict['symbols'] =        input_dict.get('symbols',        None)
    
    iprPy.input.axes(input_dict)
    iprPy.input.atomshift(input_dict)
    
    input_dict['sizemults'] =      input_dict.get('sizemults',     '3 3 3')
    iprPy.input.sizemults(input_dict)
    
    #these are integer terms
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 1000))
    
    #these are unitless float terms
    input_dict['strainrange'] =     float(input_dict.get('strainrange',     1e-6))
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    
    #these are terms with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-10 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    return input_dict

def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
        
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)    
    
def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-system-relax'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['strain-range'] = input_dict['strainrange']
    run_params['load_options'] = input_dict['load_options']
    
    #Copy over potential data model info
    calc['potential'] = DM()
    calc['potential']['key'] = input_dict['potential'].key
    calc['potential']['id'] = input_dict['potential'].id
    
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
        a_mult = input_dict['sizemults'][0][1] - input_dict['sizemults'][0][0]
        b_mult = input_dict['sizemults'][1][1] - input_dict['sizemults'][1][0]
        c_mult = input_dict['sizemults'][2][1] - input_dict['sizemults'][2][0]
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