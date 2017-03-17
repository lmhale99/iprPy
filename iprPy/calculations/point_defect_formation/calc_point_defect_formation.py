#!/usr/bin/env python

#Python script created by Lucas Hale

#Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
from copy import deepcopy
import glob

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
    
    #for key, value in input_dict.iteritems():
    #    print(key)
    #    print(value)
    #    print()
    #sys.exit()
    
    #Run ptd_energy to refine values
    results_dict = pointdefect(input_dict['lammps_command'], 
                               input_dict['initialsystem'], 
                               input_dict['potential'], 
                               input_dict['symbols'],
                               input_dict['pointdefect_model'],
                               mpi_command = input_dict['mpi_command'],
                               etol =        input_dict['energytolerance'], 
                               ftol =        input_dict['forcetolerance'], 
                               maxiter =     input_dict['maxiterations'], 
                               maxeval =     input_dict['maxevaluations'], 
                               dmax =        input_dict['maxatommotion'])

    #for key, value in results_dict.iteritems():
    #    print(key)
    #    print(value)
    #    print()
    #sys.exit()
    
    #Run check_ptd_config
    cutoff = 1.05*input_dict['ucell'].box.a
    results_dict.update(check_ptd_config(results_dict['system_ptd'], 
                                         input_dict['pointdefect_model'], 
                                         cutoff))
    
    #for key, value in results_dict.iteritems():
    #    print(key)
    #    print(value)
    #    print()
    #sys.exit()
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def pointdefect(lammps_command, system, potential, symbols, ptd_model, mpi_command=None,
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000, dmax=0.1):
    """
    Adds one or more point defects to a system and evaluates the defect formation energy.
    
    Arguments:
    lammps_command -- command for running LAMMPS.
    system -- atomman.System to add the point defect to.
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential.
    symbols -- list of element-model symbols for the Potential that correspond to system's atypes.
    ptd_model -- DataModelDict representation of a point defect data model.
    
    Keyword Arguments:
    mpi_command -- MPI command for running LAMMPS in parallel. Default value is None (serial run).  
    etol -- energy tolerance to use for the LAMMPS minimization. Default value is 0.0 (i.e. only uses ftol). 
    ftol -- force tolerance to use for the LAMMPS minimization. Default value is 1e-6.
    maxiter -- the maximum number of iterations for the LAMMPS minimization. Default value is 100000.
    maxeval -- the maximum number of evaluations for the LAMMPS minimization. Default value is 100000.    
    """
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'perfect.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['run_directory'] =       ''
    lammps_variables['etol'] =                etol
    lammps_variables['ftol'] =                uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] =             maxiter
    lammps_variables['maxeval'] =             maxeval
    lammps_variables['dmax'] =                dmax
    
    #Write lammps input script
    template_file = 'min.template'
    lammps_script = 'min.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    #run lammps to relax perfect.dat
    output = lmp.run(lammps_command, 'min.in', mpi_command)
    
    #Extract LAMMPS thermo data.
    E_total_base = uc.set_in_units(output.finds('PotEng')[-1], lammps_units['energy'])
    E_coh = E_total_base / system.natoms
    
    #rename log file
    shutil.move('log.lammps', 'min-perfect-log.lammps')
    
    #Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(int(output.finds('Step')[-1]))
    system_base = lmp.atom_dump.load(last_dump_file)
    system_base.box_set(vects=system.box.vects)
    lmp.atom_dump.dump(system_base, 'perfect.dump')
    
    #Add defect(s)
    system_ptd = deepcopy(system_base)
    for params in ptd_model.iterfinds('atomman-defect-point-parameters'):       
        system_ptd = am.defect.point(system_ptd, **params)
    
    #update lammps variables
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system_ptd, 'defect.dat',
                                                                 units = potential.units, 
                                                                 atom_style = potential.atom_style)
    
    #Write lammps input script
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))

    #run lammps
    output = lmp.run(lammps_command, 'min.in', mpi_command)
    
    #extract lammps thermo data
    E_total_ptd = uc.set_in_units(output.finds('PotEng')[-1], lammps_units['energy'])
    
    #rename log file
    shutil.move('log.lammps', 'min-defect-log.lammps')    
    
    #Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(int(output.finds('Step')[-1]))
    system_ptd = lmp.atom_dump.load(last_dump_file)
    system_ptd.box_set(vects=system.box.vects)
    
    #compute defect formation energy as difference between total potential energy of defect system
    #and the cohesive energy of the perfect system times the number of atoms in the defect system
    E_ptd_f = E_total_ptd - E_coh * system_ptd.natoms
    
    #Clear atom.* files and save dump files of relaxed systems
    for fname in glob.iglob(os.path.join(os.getcwd(), 'atom.*')):
        os.remove(fname)
    
    return {'E_coh':         E_coh,          'E_ptd_f':      E_ptd_f, 
            'E_total_base':  E_total_base,   'E_total_ptd':  E_total_ptd,
            'system_base':   system_base,    'system_ptd':   system_ptd,
            'dumpfile_base': 'perfect.dump', 'dumpfile_ptd': 'defect.dump'}

def check_ptd_config(system, ptd_model, cutoff, tol=1e-5):
    """
    Evaluates a relaxed system containing a point defect to determine if the defect 
    structure has transformed to a different configuration.
    
    Arguments:
    system -- atomman.System containing the point defect(s)
    ptd_model -- DataModelDict representation of a point defect data model
    cutoff -- cutoff to use for identifying atoms nearest to the defect's position
    
    Keyword Argument:
    tol -- tolerance to use for identifying if a defect has reconfigured. Default value is 1e-5.
    """
    
    #Extract the parameter sets
    params = deepcopy(ptd_model.finds('atomman-defect-point-parameters'))
    
    #if there is only one set, use that set
    if len(params) == 1:
        params = params[0]
        
    #if there are two sets (divacancy), use the first and average position
    elif len(params) == 2:
        di_pos = (np.array(params[0]['pos']) + np.array(params[1]['pos'])) / 2
        params = params[0]
        params['pos'] = di_pos
    
    #More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')
    
    #Initially set has_reconfigured to False
    has_reconfigured = False
    
    #Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.view['pos'], params['pos']) 
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    
    #calculate centrosummation by summing up the positions of the close atoms
    centrosummation = np.sum(pos_vects[pos_mags < cutoff], axis=0)
    
    if not np.allclose(centrosummation, np.zeros(3), atol=tol):
        has_reconfigured = True
        
    #Calculate shift of defect atom's position if interstitial or substitutional
    if params['ptd_type'] == 'i' or params['ptd_type'] == 's':
        position_shift = system.dvect(system.natoms-1, params['pos'])
       
        if not np.allclose(position_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'position_shift':   position_shift}
        
    #Investigate if dumbbell vector has shifted direction 
    elif params['ptd_type'] == 'db':
        db_vect = params['db_vect'] / np.linalg.norm(params['db_vect'])
        new_db_vect = system.dvect(system.natoms-2, system.natoms-1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
    
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'db_vect_shift':    db_vect_shift}   
    
    else:
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation}

def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    #Read input values from defect model (if given)
    read_pointdefect_model(input_dict)
    
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
       
    input_dict['sizemults'] =      input_dict.get('sizemults',     '3 3 3')
    iprPy.input.sizemults(input_dict)
    
    #these are integer terms
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  100000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
        
    #these are unitless float terms
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    
    #these are terms with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-6 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    return input_dict

def read_pointdefect_model(input_dict):
    """Read/handle parameters associated with the point defect"""
    
    #Check if stackingfault_model was defined
    if 'pointdefect_model' in input_dict:
        assert 'pointdefect_type'           not in input_dict, 'pointdefect_type and pointdefect_model cannot both be supplied'
        assert 'pointdefect_atype'          not in input_dict, 'pointdefect_atype and pointdefect_model cannot both be supplied'
        assert 'pointdefect_pos'            not in input_dict, 'pointdefect_pos and pointdefect_model cannot both be supplied'
        assert 'pointdefect_aid'            not in input_dict, 'pointdefect_aid and pointdefect_model cannot both be supplied'
        assert 'pointdefect_dumbbell_vect'  not in input_dict, 'pointdefect_dumbbell_vect and pointdefect_model cannot both be supplied'
        assert 'pointdefect_scale'          not in input_dict, 'pointdefect_scale and pointdefect_model cannot both be supplied'
    
        #Load pointdefect_model
        try:
            with open(input_dict['pointdefect_model']) as f:
                input_dict['pointdefect_model'] = DM(f).find('point-defect-parameters')
        except:
            raise ValueError('Invalid pointdefect_model')
        input_dict['pointdefect_params'] = DM()
    else:
        
        #Build pointdefect_model based on input parameters
        input_dict['pointdefect_model'] = DM()
        input_dict['pointdefect_model']['atomman-defect-point-parameters'] = ptd_params = DM()

        if 'pointdefect_type' in input_dict:            
            if   input_dict['pointdefect_type'].lower() in ['v', 'vacancy']:
                ptd_params['ptd_type'] = 'v'
            elif input_dict['pointdefect_type'].lower() in ['i', 'interstitial']:
                ptd_params['ptd_type'] = 'i'
            elif input_dict['pointdefect_type'].lower() in ['s', 'substitutional']:
                ptd_params['ptd_type'] = 's'
            elif input_dict['pointdefect_type'].lower() in ['d', 'db', 'dumbbell']:
                ptd_params['ptd_type'] = 'db'  
            else:
                raise ValueError('invalid pointdefect_type')
        if 'pointdefect_atype' in input_dict:           
            ptd_params['atype'] = int(input_dict['pointdefect_atype'])
        if 'pointdefect_pos' in input_dict:             
            ptd_params['pos'] = list(np.array(input_dict['pointdefect_pos'].split(), dtype=float))
        if 'pointdefect_aid' in input_dict:             
            ptd_params['aid'] = int(input_dict['pointdefect_aid'])
        if 'pointdefect_dumbbell_vect' in input_dict:   
            ptd_params['db_vect'] =  list(np.array(input_dict['pointdefect_dumbbell_vect'].split(), dtype=float))
        ptd_params['scale'] = iprPy.input.boolean(input_dict.get('pointdefect_scale', False))

def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
        
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)
    
    input_pointdefect(input_dict)
    
def input_pointdefect(input_dict):
    
    #Unscale vector parameters relative to ucell
    for params in input_dict['pointdefect_model'].iteraslist('atomman-defect-point-parameters'):
        if 'scale' in params and params['scale'] is True:
            if 'pos' in params:
                params['pos'] = list(input_dict['ucell'].unscale(params['pos']))
            if 'db_vect' in params:
                params['db_vect'] = list(input_dict['ucell'].unscale(params['db_vect']))
            params['scale'] = False

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-point-defect-formation'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['load_options'] = input_dict['load_options']
    
    run_params['energytolerance']    = input_dict['energytolerance']
    run_params['forcetolerance']     = input_dict['forcetolerance']
    run_params['maxiterations']  = input_dict['maxiterations']
    run_params['maxevaluations'] = input_dict['maxevaluations']
    run_params['maxatommotion']      = input_dict['maxatommotion']
    
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
    
    #Save data model of the initial ucell
    calc['point-defect-parameters'] = input_dict['pointdefect_model']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = results_dict['dumpfile_base']
        calc['defect-free-system']['artifact']['format'] = 'atom_dump'
        calc['defect-free-system']['symbols'] = input_dict['symbols']
        calc['defect-free-system']['potential-energy'] = DM([('value', uc.get_in_units(results_dict['E_total_base'], 
                                                                                        input_dict['energy_unit'])), 
                                                             ('unit', input_dict['energy_unit'])])
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['dumpfile_ptd']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']
        calc['defect-system']['potential-energy'] = DM([('value', uc.get_in_units(results_dict['E_total_ptd'], 
                                                                                  input_dict['energy_unit'])), 
                                                        ('unit', input_dict['energy_unit'])])
        
        #Save the calculation results
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['E_coh'], 
                                                                input_dict['energy_unit'])), 
                                      ('unit', input_dict['energy_unit'])])
        
        calc['number-of-atoms'] = results_dict['system_ptd'].natoms
        calc['defect-formation-energy'] = DM([('value', uc.get_in_units(results_dict['E_ptd_f'], 
                                                                        input_dict['energy_unit'])), 
                                              ('unit', input_dict['energy_unit'])])
        
        calc['reconfiguration-check'] = r_c = DM()
        r_c['has_reconfigured'] = results_dict['has_reconfigured']
        r_c['centrosummation'] = list(results_dict['centrosummation'])
        if 'position_shift' in results_dict:
            r_c['position_shift'] = list(results_dict['position_shift'])
        elif 'db_vect_shift' in results_dict:
            r_c['db_vect_shift'] = list(results_dict['db_vect_shift'])

    return output

            
if __name__ == '__main__':
    main(*sys.argv[1:])    