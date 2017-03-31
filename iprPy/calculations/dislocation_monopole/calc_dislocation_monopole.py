#!/usr/bin/env python

#Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import glob
import shutil
import random
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

calc_name = os.path.splitext(os.path.basename(__file__))[0]
assert calc_name[:5] == 'calc_', 'Calculation file name must start with "calc_"'
calc_type = calc_name[5:]

def main(*args):
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])
    
    interpret_input(input_dict)
   
    burgers = input_dict['ucell'].box.a * np.array(input_dict['burgers'])
    bwidth = input_dict['ucell'].box.a * np.array(input_dict['boundarywidth'])

    axes = np.array([input_dict['x_axis'], input_dict['y_axis'], input_dict['z_axis']])
   
    results_dict = dislocation_monopole(input_dict['lammps_command'], 
                                        input_dict['initialsystem'], 
                                        input_dict['potential'], 
                                        input_dict['symbols'], 
                                        burgers, 
                                        input_dict['C'], 
                                        axes = axes,
                                        mpi_command = input_dict['mpi_command'], 
                                        etol =        input_dict['energytolerance'], 
                                        ftol =        input_dict['forcetolerance'], 
                                        maxiter =     input_dict['maxiterations'], 
                                        maxeval =     input_dict['maxevaluations'], 
                                        dmax =        input_dict['maxatommotion'],
                                        annealtemp =  input_dict['annealtemperature'], 
                                        randomseed =  input_dict['randomseed'], 
                                        bwidth =      bwidth, 
                                        bshape =      input_dict['boundaryshape'])
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def dislocation_monopole(lammps_command, system, potential, symbols, burgers, C, 
                         mpi_command=None, axes=None, randomseed=None,
                         etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01,
                         annealtemp=0.0, bwidth=3.0, bshape='circle'):    
    #initialize results dict
    results_dict = {}    
    
    #Save initial perfect system
    am.lammps.atom_dump.dump(system, 'base.dump')
    results_dict['base_system_file'] = 'base.dump'
    results_dict['base_system_symbols'] = symbols

    #Solve Stroh method for dislocation
    stroh = am.defect.Stroh(C, burgers, axes=axes)
    results_dict['Stroh_preln'] = stroh.preln
    results_dict['Stroh_K_tensor'] = stroh.K_tensor    
    
    #Generate dislocation system by displacing atoms according to Stroh solution
    disp = stroh.displacement(system.atoms.view['pos'])
    system.atoms.view['pos'] += disp

    system.wrap()
    
    #Apply fixed boundary conditions
    system, symbols = disl_boundary_fix(system, symbols, bwidth, bshape)
    
    #relax system
    relaxed = disl_relax(lammps_command, system, potential, symbols, 
                         mpi_command = mpi_command, 
                         annealtemp = annealtemp,
                         etol = etol, 
                         ftol = ftol, 
                         maxiter = maxiter, 
                         maxeval = maxeval)
    
    #Save relaxed dislocation system with original box vects
    system_disl = am.load('atom_dump', relaxed['finaldumpfile'])[0]

    system_disl.box_set(vects=system.box.vects, origin=system.box.origin)
    lmp.atom_dump.dump(system_disl, 'disl.dump')
    results_dict['disl_system_file'] = 'disl.dump'
    results_dict['disl_system_symbols'] = symbols
    
    results_dict['disl_system_Epot'] = relaxed['potentialenergy']
    
    #Cleanup atom.* files
    for atomfile in glob.iglob('atom.*'):
        os.remove(atomfile)
    
    return results_dict

def disl_boundary_fix(system, symbols, bwidth, bshape='circle'):
    """Create boundary region by changing atom types. Returns a new system and symbols list."""
    natypes = system.natypes
    atypes = system.atoms_prop(key='atype')
    pos = system.atoms_prop(key='pos')
    
    if bshape == 'circle':
        #find x or y bound closest to 0
        smallest_xy = min([abs(system.box.xlo), abs(system.box.xhi),
                           abs(system.box.ylo), abs(system.box.yhi)])
        
        radius = smallest_xy - bwidth
        xy_mag = np.linalg.norm(system.atoms_prop(key='pos')[:,:2], axis=1)        
        atypes[xy_mag > radius] += natypes
    
    elif bshape == 'rect':
        index = np.unique(np.hstack((np.where(pos[:,0] < system.box.xlo + bwidth),
                                     np.where(pos[:,0] > system.box.xhi - bwidth),
                                     np.where(pos[:,1] < system.box.ylo + bwidth),
                                     np.where(pos[:,1] > system.box.yhi - bwidth))))
        atypes[index] += natypes
           
    else:
        raise ValueError("Unknown boundary shape type! Enter 'circle' or 'rect'")

    new_system = deepcopy(system)
    new_system.atoms_prop(key='atype', value=atypes)
    symbols.extend(symbols)
    
    return new_system, symbols
        
def disl_relax(lammps_command, system, potential, symbols, 
               mpi_command=None, annealtemp=0.0, randomseed=None,
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000, dmax=0.01):
    """Runs LAMMPS using the disl_relax.in script for relaxing a dislocation monopole system."""
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'system.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['anneal_info'] =         anneal_info(annealtemp, randomseed, potential.units)
    lammps_variables['etol'] =    etol
    lammps_variables['ftol'] =     uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] =  maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    lammps_variables['group_move'] =          ' '.join(np.array(range(1, system.natypes//2+1), dtype=str))
    
    #Set dump_modify format based on dump_modify_version
    dump_modify_version = iprPy.tools.lammps_version.dump_modify(lammps_command)
    if dump_modify_version == 0:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    elif dump_modify_version == 1:
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    
    #Write lammps input script
    template_file = 'disl_relax.template'
    lammps_script = 'disl_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))    

    #run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object')
    
    #Extract output values
    results = {}
    results['logfile'] =         'log.lammps'
    results['initialdatafile'] = 'system.dat'
    results['initialdumpfile'] = 'atom.0'
    results['finaldumpfile'] =   'atom.%i' % output.simulations[-1]['thermo'].Step.tolist()[-1] 
    results['potentialenergy'] = uc.set_in_units(output.simulations[-1]['thermo'].PotEng.tolist()[-1], lammps_units['energy'])
    
    return results

def anneal_info(temperature=0.0, randomseed=None, units='metal'):
    """
    Generates LAMMPS commands for thermo anneal. 
    
    Keyword Arguments:
    temperature -- temperature to relax at. Default value is 0. 
    randomseed -- random number seed used by LAMMPS for velocity creation. 
                  Default value generates a new random integer every time.
    units -- LAMMPS units style to use.
    """
    #Get lammps units
    lammps_units = lmp.style.unit(units)
    
    #Return nothing if temperature is 0.0 (don't do thermo anneal)
    if temperature == 0.0:
        return ''
    
    #Generate velocity, fix nvt, and run LAMMPS command lines
    else:
        if randomseed is None: 
            randomseed = random.randint(1, 900000000)
            
        start_temp = 2 * temperature
        tdamp = 100 * lmp.style.timestep(units)
        timestep = lmp.style.timestep(units)
        info = '\n'.join(['velocity move create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
                           'fix nvt all nvt temp %f %f %f' % (temperature, temperature, tdamp),
                           'timestep %f' % (timestep),
                           'thermo 10000',
                           'run 10000'])

    return info
    
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
       
    input_dict['sizemults'] =      input_dict.get('sizemults',     '-10 10 -10 10 0 3')
    iprPy.input.sizemults(input_dict)
    
    input_dict['boundaryshape'] =  input_dict.get('boundaryshape', 'circle')
    
    #these are integer terms
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
    input_dict['randomseed'] =     int(input_dict.get('randomseed',  
                                       random.randint(1, 900000000)))
        
    #these are unitless float terms
    input_dict['energytolerance'] =   float(input_dict.get('energytolerance', 0.0))
    input_dict['annealtemperature'] = float(input_dict.get('annealtemperature', 0.0))
    input_dict['boundarywidth'] =     float(input_dict.get('boundarywidth', 3.0))
    
    #these are terms with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-6 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
                                                    
    #Check if dislocation_model was defined
    if 'dislocation_model' in input_dict:
        #Verify competing parameters are not defined
        assert 'burgers'   not in input_dict, 'burgers and dislocation_model cannot both be supplied'
        assert 'atomshift' not in input_dict, 'atomshift and dislocation_model cannot both be supplied'
        assert 'x_axis'    not in input_dict, 'x_axis and dislocation_model cannot both be supplied'
        assert 'y_axis'    not in input_dict, 'y_axis and dislocation_model cannot both be supplied'
        assert 'z_axis'    not in input_dict, 'z_axis and dislocation_model cannot both be supplied'
    else:
        input_dict['dislocation_model'] = None
        
    return input_dict
    
def interpret_dislocation_model(input_dict):
    """Read/handle parameters associated with the dislocation model (axes, burgers, and atomshift)"""
        
    #Check if dislocation_model was defined
    if input_dict['dislocation_model'] is not None:
    
        #Load dislocation_model
        try:
            with open(input_dict['dislocation_model']) as f:
                input_dict['dislocation_model'] = DM(f).find('dislocation-monopole')
        except:
            raise ValueError('Invalid dislocation_model')

        #Extract parameter values from dislocation_model 
        params = input_dict['dislocation_model']['atomman-defect-Stroh-parameters']
        input_dict['burgers'] = np.array(params['burgers'], dtype=float)
        input_dict['atomshift'] = params['atomshift']
        input_dict['x_axis'] = params['crystallographic-axes']['x-axis']
        input_dict['y_axis'] = params['crystallographic-axes']['y-axis']
        input_dict['z_axis'] = params['crystallographic-axes']['z-axis']

    #If dislocation_model is not defined
    else:
        iprPy.input.axes(input_dict)
        iprPy.input.atomshift(input_dict)
        input_dict['burgers'] = np.array(input_dict['burgers'], dtype=float)
        
def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
    
    interpret_dislocation_model(input_dict)
    
    interpret_elasticconstants_model(input_dict)
    
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)

    
def interpret_elasticconstants_model(input_dict):
    """Finds and sets elastic constants from input_dict info"""
    
    #Extract explicit elastic constants from Cij terms in input_dict
    Cdict = {}
    for key in input_dict:
        if key[0] == 'C':
            Cdict[key] = iprPy.input.value(input_dict, key, default_unit=input_dict['pressure_unit'])
    
    #Build ElasticConstants from Cij terms 
    if len(Cdict) > 0:
        assert 'elastic_constants_model' not in input_dict, 'Cij values and elastic_constants_model cannot both be specified.'
        input_dict['elastic_constants_model'] = None 
        input_dict['C'] = am.ElasticConstants(**Cdict)
    
    #If no Cij terms defined check for elasticonstants_model
    else:
        #Use load file if elasticconstants_model not defined
        input_dict['elasticconstants_model'] = input_dict.get('elasticconstants_model', input_dict['load'].split()[1])
        
        with open(input_dict['elasticconstants_model']) as f:
            C_model = DM(f)
            
        try:
            input_dict['elasticconstants_model'] = DM([('elastic-constants', C_model.find('elastic-constants'))])
            input_dict['C'] = am.ElasticConstants(model=input_dict['elasticconstants_model'])
        except:
            input_dict['elasticconstants_model'] = None 
            input_dict['C'] = None 

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-dislocation-monopole'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = calc_name
    
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['load_options'] = input_dict['load_options']
    
    run_params['energytolerance'] = input_dict['energytolerance']
    run_params['forcetolerance'] =  input_dict['forcetolerance']
    run_params['maxiterations'] =   input_dict['maxiterations']
    run_params['maxevaluations'] =  input_dict['maxevaluations']
    run_params['maxatommotion'] =   input_dict['maxatommotion']
    
    run_params['annealtemperature'] = input_dict['annealtemperature']
    
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
    
    #Save defect parameters
    calc['dislocation-monopole'] = disl = DM()
    if input_dict['dislocation_model'] is not None:
        disl['key'] = input_dict['dislocation_model']['key']
        disl['id'] =  input_dict['dislocation_model']['id']
    
    disl['system-family'] = input_dict['system_family']
    disl['atomman-defect-Stroh-parameters'] = adsp = DM() 
    adsp['crystallographic-axes'] = DM()
    adsp['crystallographic-axes']['x-axis'] = input_dict['x_axis']
    adsp['crystallographic-axes']['y-axis'] = input_dict['y_axis']
    adsp['crystallographic-axes']['z-axis'] = input_dict['z_axis']
    adsp['burgers'] = list(input_dict['burgers'])
    adsp['atomshift'] = input_dict['atomshift']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['elastic-constants'] = input_dict['C'].model(unit=input_dict['pressure_unit'])['elastic-constants']
    
        calc['base-system'] = DM()
        calc['base-system']['artifact'] = DM()
        calc['base-system']['artifact']['file'] = results_dict['base_system_file']
        calc['base-system']['artifact']['format'] = 'atom_dump'
        calc['base-system']['symbols'] = results_dict['base_system_symbols']
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['disl_system_file']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = results_dict['disl_system_symbols']
        
        calc['potential-energy'] = DM()
        calc['potential-energy']['value'] = uc.get_in_units(results_dict['disl_system_Epot'], 
                                           input_dict['energy_unit']) 
        calc['potential-energy']['unit'] = input_dict['energy_unit']
                                                        
        calc['Stroh-pre-ln-factor'] = DM()
        calc['Stroh-pre-ln-factor']['value'] = uc.get_in_units(results_dict['Stroh_preln'], 
                                              input_dict['energy_unit']+'/'+input_dict['length_unit'])
        calc['Stroh-pre-ln-factor']['unit'] = input_dict['energy_unit']+'/'+input_dict['length_unit']
        
        calc['Stroh-K-tensor'] = []
        Kij = results_dict['Stroh_K_tensor']
        for i in xrange(3):
            for j in xrange(i,3):
                K = DM()
                K['coefficient'] = DM()
                K['coefficient']['value'] = uc.get_in_units(Kij[i,j], input_dict['pressure_unit'])
                K['coefficient']['unit'] = input_dict['pressure_unit']
                K['ij'] = '%i %i' % (i+1, j+1)
                calc['Stroh-K-tensor'].append(K)

    return output

if __name__ == '__main__':
    main(*sys.argv[1:])    