#!/usr/bin/env python

#Python script created by Lucas Hale and Norman Luu.

#Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
from copy import deepcopy
from multiprocessing import Pool

#http://www.numpy.org/
import numpy as np 

import pandas as pd

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

def main(pool, *args):
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])

    interpret_input(input_dict)
    
    results_dict = stackingfault_map(input_dict['lammps_command'], 
                                     input_dict['initialsystem'], 
                                     input_dict['potential'], 
                                     input_dict['symbols'], 
                                     pool =          pool,
                                     keepatomfiles = input_dict['keepatomfiles'],
                                     mpi_command =   input_dict['mpi_command'], 
                                     etol =          input_dict['energytolerance'], 
                                     ftol =          input_dict['forcetolerance'], 
                                     maxiter =       input_dict['maxiterations'], 
                                     maxeval =       input_dict['maxevaluations'], 
                                     dmax =          input_dict['maxatommotion'],
                                     planeaxis =     input_dict['stackingfault_planeaxis'], 
                                     planepos =      input_dict['planepos'],
                                     numshifts1 =    input_dict['stackingfault_numshifts1'],
                                     numshifts2 =    input_dict['stackingfault_numshifts2'],
                                     shiftvector1 =  input_dict['shiftvector1'],
                                     shiftvector2 =  input_dict['shiftvector2'])

    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def stackingfault_map(lammps_command, system, potential, symbols, 
                      shiftvector1, shiftvector2,
                      mpi_command=None, pool=None, keepatomfiles=True,
                      planeaxis='z', planepos=0.5, 
                      numshifts1=11, numshifts2=11,
                      etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01):
    """
    Computes a 2D generalized stacking fault map for a specific plane. First,
    free surfaces parallel to the cut plane are created by removing periodic
    boundaries, then the atoms above the cut plane are shifted multiple times.
    The underlying simulations allow only atomic relaxation perpendicular to 
    the stacking fault plane.
    
    Arguments:
    lammps_command -- directory location for lammps executable.
    system -- atomman.System in which the stacking fault will be added.
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential.
    symbols -- list of element-model symbols for the Potential that correspond
               to the System's atypes.
    shiftvector1 -- 3D vector (length units) corresponding to one period of the
                    stacking fault along vector's direction. The vector must be
                    in the cut plane (i.e. no component along the planeaxis). 
                    The two shiftvectors cannot be parallel, but they don't 
                    have to be perpendicular.
    shiftvector2 -- 3D vector (length units) corresponding to one period of the
                    stacking fault along vector's direction. The vector must be
                    in the cut plane (i.e. no component along the planeaxis). 
                    The two shiftvectors cannot be parallel, but they don't 
                    have to be perpendicular.
                    
    Keyword Arguments:
    mpi_command -- mpi command to use for running LAMMPS in parallel. Default 
                   value is None (run serially).
    pool -- multiprocessing pool to which the running of the simulations is to
            be distributed to. Allows multiple points to be simultaneously 
            simulated. Default value is None (run one LAMMPS simulation at a 
            time).
    keepatomfiles -- Boolean indicating if the atom data and dump files from 
                     the simulations are kept or deleted. Default value is True
                     (atom files are not deleted).
    planeaxis -- the Cartesian axis (x, y, or z) to use as the normal to the 
                 cut plane. For non-orthogonal systems, only the box vector 
                 corresponding to the planeaxis (a<->x, b<->y, c<->z) can have 
                 a component along planeaxis. Default value is 'z'.
    planepos -- the fractional distance of the system's box along planeaxis 
                where the cut plane will be positioned. Default value is 0.5.
    numshifts1 -- number of shift steps to divide up shiftvector1 by. Default
                  value is 11.
    numshifts2 -- number of shift steps to divide up shiftvector2 by. Default
                  value is 11.
    etol -- the LAMMPS minimization energy tolerance (unitless) to use. Default
            value is 0.0 (energy not considered). 
    ftol -- the LAMMPS minimization force tolerance (in force units) to use. 
            Default value is 0.0 (force not considered). 
    maxiter -- the max number of LAMMPS minimization iterations. Default value
               is 1000.
    maxeval -- the max number of LAMMPS minimization evaluations. Default value
               is 10000.
    dmax -- the maximum distance (in length units) an atom can move during a 
            minimization step. Default is 0.01.    
    """
    
    #Set up options based on planeaxis
    if   planeaxis == 'x':
        #Assert system is compatible with planeaxis value
        if system.box.xy != 0.0 or system.box.xz != 0.0:
            raise ValueError("box tilts xy and xz must be 0 for planeaxis='x'")
        
        #Specify cutindex
        cutindex = 0
        
        #Identify atoms above cut plane
        topmap = system.atoms.view['pos'][:, cutindex] > (system.box.xlo + system.box.lx * planepos)
        
        #Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
    
    elif planeaxis == 'y':
        #Assert system is compatible with planeaxis value
        if system.box.yz != 0.0:
            raise ValueError("box tilt yz must be 0 for planeaxis='y'")
        
        #Specify cutindex
        cutindex = 1
        
        #Identify atoms above cut plane
        topmap = system.atoms.view['pos'][:, cutindex] > (system.box.ylo + system.box.ly * planepos)
        
        #Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
    
    elif planeaxis == 'z': 
        #Assert system is compatible with planeaxis value
        #LAMMPS systems are already compatible 
        
        #Specify cutindex
        cutindex = 2
        
        #Identify atoms above cut
        topmap = system.atoms.view['pos'][:, cutindex] > (system.box.zlo + system.box.lz * planepos)
        
        #Compute fault area
        faultarea = np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
    
    else: 
        raise ValueError('Invalid planeaxis')
    
    #Assert shiftvectors are in cut plane
    if shiftvector1[cutindex] != 0.0:
        raise ValueError('shiftvector1 must be in cut plane')
    if shiftvector2[cutindex] != 0.0:
        raise ValueError('shiftvector2 must be in cut plane')
    
    #Create free surface parallel to cut plane
    system.pbc = [True, True, True]
    system.pbc[cutindex] = False
    
    #Create results list
    results_list = []

    #Build calc_kwargs dictionary (these don't change)
    calc_kwargs = {'mpi_command': mpi_command, 'keepatomfiles':keepatomfiles,
                   'etol':etol, 'ftol':ftol, 
                   'maxiter':maxiter, 'maxeval':maxeval, 
                   'dmax':dmax, 'planeaxis':planeaxis}
    
    #Loop over all shift combinations
    shifts1, shifts2 = np.meshgrid(np.linspace(0, 1, numshifts1), 
                                   np.linspace(0, 1, numshifts2))
    for shift1, shift2 in zip(shifts1.flat, shifts2.flat):
        
        #Build calc_args list
        calc_args = (lammps_command, system, potential, symbols,
                     shiftvector1, shiftvector2, shift1, shift2, topmap)
        
        if pool is not None:
            #Submit sfworker call to pool
            results_list.append(pool.apply_async(sfworker, args=calc_args, kwds=calc_kwargs))
        else:
            #Call sfworker if no pool
            results_list.append(sfworker(*calc_args, **calc_kwargs))
        
    if pool is not None:
        #Finish running and get results 
        pool.close()
        pool.join()
        for i in xrange(len(results_list)):
            results_list[i] = results_list[i].get()
        
    df = pd.DataFrame(results_list)
    
    noshift = df[(np.isclose(df.shift1, 0.0, atol=1e-10, rtol=0.0) & 
                  np.isclose(df.shift2, 0.0, atol=1e-10, rtol=0.0))]
    assert len(noshift) == 1
    
    results_dict = {}
    results_dict['shift1'] = df.shift1.tolist()
    results_dict['shift2'] = df.shift2.tolist()
    results_dict['sfenergy'] = list((df.potentialenergy.values - 
                                     noshift.potentialenergy.values) / faultarea)
    results_dict['deltadisp'] = list((df.displacement.values - 
                                      noshift.displacement.values))
    
    return results_dict

def sfworker(lammps_command, system, potential, symbols,
             shiftvector1, shiftvector2, shift1, shift2, topmap,
             mpi_command=None, keepatomfiles=True,
             etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01,
             planeaxis='z'):
    """Workers for running relax_sfsystem"""
    
    if   planeaxis == 'x': cutindex = 0
    elif planeaxis == 'y': cutindex = 1  
    elif planeaxis == 'z': cutindex = 2
    
    #Initialize results_dict
    results_dict = {}
    results_dict['shift1'] = shift1
    results_dict['shift2'] = shift2
    
    #Generate subdirectory name
    dirname = 'a%.10f-b%.10f' % (shift1, shift2)
    
    #Test if subdirectory already exists
    if not os.path.isdir(dirname): os.mkdir(dirname)
    
    #Generate stacking fault by shifting atoms above the cut plane
    isystem = deepcopy(system)
    planeshift = shift1 * shiftvector1 + shift2 * shiftvector2
    isystem.atoms.view['pos'][topmap] += planeshift
    
    #Call relax_sfsystem
    stackingfault = relax_sfsystem(lammps_command, isystem, potential, symbols, 
                                   run_directory=dirname, mpi_command=mpi_command,
                                   etol=etol, ftol=ftol, maxiter=maxiter, 
                                   maxeval=maxeval,dmax=dmax, planeaxis=planeaxis)
    
    #Extract results from system with stacking fault
    stackingfaultsystem = am.load('atom_dump', stackingfault['finaldumpfile'])[0]
    results_dict['potentialenergy'] = stackingfault['potentialenergy']
    os.remove(os.path.join(dirname, 'atom.0'))
    os.remove(stackingfault['finaldumpfile']+'.json')
    
    if keepatomfiles is True:
        shutil.move(stackingfault['finaldumpfile'], os.path.join(dirname, 'stackingfault.dump'))
    elif keepatomfiles is False:
        os.remove(os.path.join(dirname, 'system.dat'))
        os.remove(stackingfault['finaldumpfile'])
        
    
    #Find center of mass difference in top/bottom planes
    if   planeaxis == 'x': cutindex = 0
    elif planeaxis == 'y': cutindex = 1  
    elif planeaxis == 'z': cutindex = 2
    results_dict['displacement'] = (stackingfaultsystem.atoms.view['pos'][topmap,  cutindex].mean() -
                                    stackingfaultsystem.atoms.view['pos'][~topmap, cutindex].mean())
    
    return results_dict
    
def relax_sfsystem(lammps_command, system, potential, symbols, 
                   run_directory='', mpi_command=None, 
                   etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01,
                   planeaxis=None):
    """
    Sets up and runs the min LAMMPS script for statically relaxing a system
    """
    
    #Ensure all atoms are within the system's box
    system.wrap()
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
   
    #Define lammps variables
    lammps_variables = {}
    
    #Generate system and pair info
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, os.path.join(run_directory, 'system.dat'), 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    
    #Generate fix setforce command
    if   planeaxis == None: lammps_variables['fix_cut_setforce'] = ''
    elif planeaxis == 'x':  lammps_variables['fix_cut_setforce'] = 'fix cut all setforce NULL 0 0'
    elif planeaxis == 'y':  lammps_variables['fix_cut_setforce'] = 'fix cut all setforce 0 NULL 0'
    elif planeaxis == 'z':  lammps_variables['fix_cut_setforce'] = 'fix cut all setforce 0 0 NULL'
    else: raise ValueError('Invalid planeaxis')
    
    #Pass in run parameters
    if len(run_directory) > 0 and run_directory[-1] != '/':  
        lammps_variables['run_directory'] = run_directory + '/'
    else:
        lammps_variables['run_directory'] = run_directory
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    #Write lammps input script
    template_file = 'sfmin.template'
    lammps_script = os.path.join(run_directory, 'sfmin.in')
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    #run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object', 
                     logfile=os.path.join(run_directory, 'log.lammps'))
    
    #Extract output values
    results = {}
    results['logfile'] =         os.path.join(run_directory, 'log.lammps')
    results['initialdatafile'] = os.path.join(run_directory, 'system.dat')
    results['initialdumpfile'] = os.path.join(run_directory, 'atom.0')
    results['finaldumpfile'] =   os.path.join(run_directory, 'atom.%i' % output.simulations[-1]['thermo'].Step.tolist()[-1])
    results['potentialenergy'] = uc.set_in_units(output.simulations[-1]['thermo'].PotEng.tolist()[-1], lammps_units['energy'])
    
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
       
    input_dict['sizemults'] =      input_dict.get('sizemults',     '3 3 3')
    iprPy.input.sizemults(input_dict)
    
    #these are boolean terms
    input_dict['keepatomfiles'] = iprPy.input.boolean(input_dict.get('keepatomfiles', True))
    
    #these are integer terms
    input_dict['stackingfault_numshifts1'] = int(input_dict.get('stackingfault_numshifts1', 11))
    input_dict['stackingfault_numshifts2'] = int(input_dict.get('stackingfault_numshifts2', 11))
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
    
    #Check if stackingfault_model was defined
    if 'stackingfault_model' in input_dict:
        #Verify competing parameters are not defined
        assert 'atomshift' not in input_dict, 'atomshift and stackingfault_model cannot both be supplied'
        assert 'x_axis'    not in input_dict, 'x_axis and stackingfault_model cannot both be supplied'
        assert 'y_axis'    not in input_dict, 'y_axis and stackingfault_model cannot both be supplied'
        assert 'z_axis'    not in input_dict, 'z_axis and stackingfault_model cannot both be supplied'
        assert 'stackingfault_planeaxis'    not in input_dict, 'stackingfault_planeaxis and stackingfault_model cannot both be supplied'
        assert 'stackingfault_planepos'     not in input_dict, 'stackingfault_planepos and stackingfault_model cannot both be supplied'
        assert 'stackingfault_shiftvector1' not in input_dict, 'stackingfault_shiftvector1 and stackingfault_model cannot both be supplied'
        assert 'stackingfault_shiftvector2' not in input_dict, 'stackingfault_shiftvector2 and stackingfault_model cannot both be supplied'
    else:
        input_dict['stackingfault_model'] = None
        input_dict['stackingfault_planeaxis'] = input_dict.get('stackingfault_planeaxis', 'z')
        input_dict['stackingfault_planepos'] = float(input_dict.get('stackingfault_planepos', 0.5))
        input_dict['stackingfault_shiftvector1'] = list(np.array(input_dict['stackingfault_shiftvector1'].strip().split(), dtype=float))
        input_dict['stackingfault_shiftvector2'] = list(np.array(input_dict['stackingfault_shiftvector2'].strip().split(), dtype=float))
        
        
    return input_dict

def interpret_stackingfault_model(input_dict):
    """Read/handle parameters associated with the stacking fault"""
    
    #Check if stackingfault_model was defined
    if input_dict['stackingfault_model'] is not None:
        
        #Load stackingfault_model
        try:
            with open(input_dict['stackingfault_model']) as f:
                input_dict['stackingfault_model'] = DM(f).find('stacking-fault')
        except:
            raise ValueError('Invalid stackingfault_model')
            
        #Extract parameter values from stackingfault_model
        params = input_dict['stackingfault_model']['atomman-stacking-fault-parameters']
        input_dict['x_axis'] = params['crystallographic-axes']['x-axis']
        input_dict['y_axis'] = params['crystallographic-axes']['y-axis']
        input_dict['z_axis'] = params['crystallographic-axes']['z-axis']
        input_dict['atomshift'] = params['atomshift']
        input_dict['stackingfault_planeaxis'] = params['plane-axis']
        input_dict['stackingfault_planepos'] = params['plane-position']
        input_dict['stackingfault_shiftvector1'] = list(np.asarray(params['shift-vector-1']))
        input_dict['stackingfault_shiftvector2'] = list(np.asarray(params['shift-vector-2']))
    
    #If stackingfault_model is not defined
    else:
        iprPy.input.axes(input_dict)
        iprPy.input.atomshift(input_dict)
        
def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
    
    interpret_stackingfault_model(input_dict)
    
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)
    
    input_stackingfault(input_dict)
    
def input_stackingfault(input_dict):
    
    #Check parameter compatibilities
    assert len(input_dict['stackingfault_shiftvector1']) == 3, 'invalid stackingfault_shiftvector1'
    assert len(input_dict['stackingfault_shiftvector2']) == 3, 'invalid stackingfault_shiftvector2'
    
    #Pull important parameters out of input_dict
    axes_array = np.array([input_dict['x_axis'], input_dict['y_axis'], input_dict['z_axis']])
    T = am.tools.axes_check(axes_array)
    ucell = input_dict['ucell']
    initialsystem = input_dict['initialsystem']
    sizemults = input_dict['sizemults']
    planepos = input_dict['stackingfault_planepos']
    planeaxis = input_dict['stackingfault_planeaxis']
     
    #Convert from crystallographic axes to Cartesian axes
    input_dict['shiftvector1'] = (input_dict['stackingfault_shiftvector1'][0] * ucell.box.avect + 
                                  input_dict['stackingfault_shiftvector1'][1] * ucell.box.bvect + 
                                  input_dict['stackingfault_shiftvector1'][2] * ucell.box.cvect)
    
    input_dict['shiftvector2'] = (input_dict['stackingfault_shiftvector2'][0] * ucell.box.avect + 
                                  input_dict['stackingfault_shiftvector2'][1] * ucell.box.bvect + 
                                  input_dict['stackingfault_shiftvector2'][2] * ucell.box.cvect)
    
    #Transform using axes
    input_dict['shiftvector1'] = T.dot(input_dict['shiftvector1'])
    input_dict['shiftvector2'] = T.dot(input_dict['shiftvector2'])
    
        
    #define planepos shift function
    def shift_planepos(p, m):
        """This shifts planepos, p, based on system multiplier, m"""
        #If m is odd, keep p=0.5 at 0.5 
        if m % 2 == 1: return (p + (m-1) * 0.5) / m        
        #If m is even, keep p=0.0 at 0.5
        else:          return (2 * p + m) / (2 * m)
    
    if   planeaxis == 'x':
        if system.box.xy != 0.0 or system.box.xz != 0.0: raise ValueError("box tilts xy and xz must be 0 for stackingfault_planeaxis='x'")
        input_dict['planepos'] = shift_planepos(planepos, sizemults[0][1] - sizemults[0][0])
        
    elif planeaxis == 'y':
        if system.box.yz != 0.0: raise ValueError("box tilt yz must be 0 for stackingfault_planeaxis='y'")
        input_dict['planepos'] = shift_planepos(planepos, sizemults[1][1] - sizemults[1][0])
    
    elif planeaxis == 'z': 
        input_dict['planepos'] = shift_planepos(planepos, sizemults[2][1] - sizemults[2][0])
    
    else: raise ValueError('Invalid stackingfault_planeaxis')
    
    
def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-generalized-stacking-fault'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = calc_name
    
    #Save run parameters
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['load_options'] = input_dict['load_options']
    
    run_params['energytolerance']          = input_dict['energytolerance']
    run_params['forcetolerance']           = input_dict['forcetolerance']
    run_params['maxiterations']            = input_dict['maxiterations']
    run_params['maxevaluations']           = input_dict['maxevaluations']
    run_params['maxatommotion']            = input_dict['maxatommotion']
    run_params['stackingfault_numshifts1'] = input_dict['stackingfault_numshifts1']
    run_params['stackingfault_numshifts2'] = input_dict['stackingfault_numshifts2']
    
    
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
    
    #Save defect model information
    calc['stacking-fault'] = sf = DM()
    
    if input_dict['stackingfault_model'] is not None:
        sf['key'] = input_dict['stackingfault_model']['key']
        sf['id'] =  input_dict['stackingfault_model']['id']
    else:
        sf['key'] = None
        sf['id'] =  None
    
    sf['system-family'] = input_dict['system_family']
    sf['atomman-stacking-fault-parameters'] = asfp = DM()    
    asfp['crystallographic-axes'] = DM()
    asfp['crystallographic-axes']['x-axis'] = input_dict['x_axis']
    asfp['crystallographic-axes']['y-axis'] = input_dict['y_axis']
    asfp['crystallographic-axes']['z-axis'] = input_dict['z_axis'] 
    asfp['atomshift'] =      input_dict['atomshift']
    asfp['plane-axis'] =     input_dict['stackingfault_planeaxis']
    asfp['plane-position'] = input_dict['stackingfault_planepos']
    asfp['shift-vector-1'] = input_dict['stackingfault_shiftvector1']
    asfp['shift-vector-2'] = input_dict['stackingfault_shiftvector2']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:        
        #Save the stacking fault energy map
        calc['stacking-fault-relation'] = DM()
        calc['stacking-fault-relation']['shift-vector-1-fraction'] = results_dict['shift1']
        calc['stacking-fault-relation']['shift-vector-2-fraction'] = results_dict['shift2']
        calc['stacking-fault-relation']['energy'] = DM()
        calc['stacking-fault-relation']['energy']['value'] = list(uc.get_in_units(results_dict['sfenergy'], 
                                                            input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2'))
        calc['stacking-fault-relation']['energy']['unit'] = input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2'
        calc['stacking-fault-relation']['plane-separation'] = DM()
        calc['stacking-fault-relation']['plane-separation']['value'] = list(uc.get_in_units(results_dict['deltadisp'], 
                                                                      input_dict['length_unit']))
        calc['stacking-fault-relation']['plane-separation']['unit'] = input_dict['length_unit']

    return output
        
if __name__ == '__main__':
    pool = Pool()
    #pool = None
    main(pool, *sys.argv[1:])     
    
