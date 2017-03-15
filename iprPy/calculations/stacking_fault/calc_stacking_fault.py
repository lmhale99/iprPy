#!/usr/bin/env python

#Python script created by Lucas Hale and Norman Luu.

#Standard library imports
from __future__ import print_function, division
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
    
    results_dict = stackingfault_point(input_dict['lammps_command'], 
                                       input_dict['initialsystem'], 
                                       input_dict['potential'], 
                                       input_dict['symbols'], 
                                       mpi_command =  input_dict['mpi_command'], 
                                       etol =         input_dict['energytolerance'], 
                                       ftol =         input_dict['forcetolerance'], 
                                       maxiter =      input_dict['maxiterations'], 
                                       maxeval =      input_dict['maxevaluations'], 
                                       dmax =         input_dict['maxatommotion'],
                                       planeaxis =    input_dict['stackingfault_planeaxis'], 
                                       planepos =     input_dict['planepos'], 
                                       planeshift =   input_dict['planeshift'])
    
    print('a b shift =       ', input_dict['stackingfault_shift'])
    print('xyz shift =       ', input_dict['planeshift'])
    print('gsf (eV/A^2) =    ', results_dict['stackingfault_energy'])
    print('normal shift (A) =', results_dict['deltadisp'])
    
    #Save data model of results 
    results = data_model(input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def stackingfault_point(lammps_command, system, potential, symbols, 
                        mpi_command=None, 
                        planeaxis='z', planepos=0.5, planeshift=[0.0, 0.0, 0.0],
                        etol=0.0, ftol=0.0, maxiter=1000, maxeval=10000, 
                        dmax=0.01):
    """
    Calculates the stacking fault energy for a specific planar shift of atoms. 
    First, free surfaces parallel to the cut plane are created by removing 
    periodic boundaries, then the atoms above the cut plane are shifted by the
    specified vector amount. The underlying simulation allows only atomic
    relaxation perpendicular to the stacking fault plane. 
    
    Arguments:
    lammps_command -- directory location for lammps executable.
    system -- atomman.System in which the stacking fault will be added.
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential.
    symbols -- list of element-model symbols for the Potential that correspond
               to the System's atypes.
    
    Keyword Arguments:
    mpi_command -- mpi command to use for running LAMMPS in parallel. Default 
                   value is None (run serially).
    planeaxis -- the Cartesian axis (x, y, or z) to use as the normal to the 
                 cut plane. For non-orthogonal systems, only the box vector 
                 corresponding to the planeaxis (a<->x, b<->y, c<->z) can have 
                 a component along planeaxis. Default value is 'z'.
    planepos -- the fractional distance of the system's box along planeaxis 
                where the cut plane will be positioned. Default value is 0.5.
    planeshift -- the 3D vector (in length units) by which to shift the atoms 
                  of system that are located above the cut plane. The vector
                  must be in the cut plane (i.e. no component along the 
                  planeaxis). Default value is [0.0, 0.0, 0.0].
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
    
    #Initialize results dictionary
    results_dict = {}
    
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
    
    #Assert planeshift is in cut plane
    if planeshift[cutindex] != 0.0:
        raise ValueError('planeshift must be in cut plane')
    
    #Create free surface parallel to cut plane
    system.pbc = [True, True, True]
    system.pbc[cutindex] = False
    
    #Evaluate zero shift system
    zeroshift = relax_sfsystem(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                               etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax, 
                               planeaxis=planeaxis)
    
    #Extract results from zero shift system
    shutil.move(zeroshift['finaldumpfile'], 'zeroshift.dump')
    shutil.move('log.lammps', 'zeroshift-log.lammps')
    results_dict['zeroshift_system_file'] = 'zeroshift.dump'
    zeroshiftsystem = am.load('atom_dump', results_dict['zeroshift_system_file'])[0]
    
    #Find center of mass difference in top/bottom planes
    initialdisp = (zeroshiftsystem.atoms.view['pos'][topmap,  cutindex].mean() - 
                   zeroshiftsystem.atoms.view['pos'][~topmap, cutindex].mean())

    #Generate stacking fault by shifting atoms above the cut plane
    system.atoms.view['pos'][topmap] += planeshift
    
    #Evaluate system with stacking fault
    stackingfault = relax_sfsystem(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                                 etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax, 
                                 planeaxis=planeaxis)
    
    #Extract results from system with stacking fault
    shutil.move(stackingfault['finaldumpfile'], 'stackingfault.dump')
    shutil.move('log.lammps', 'stackingfault-log.lammps')
    results_dict['stackingfault_system_file'] = 'stackingfault.dump'
    stackingfaultsystem = am.load('atom_dump', results_dict['stackingfault_system_file'])[0]
    results_dict['stackingfault_energy'] = (stackingfault['potentialenergy'] - zeroshift['potentialenergy']) / faultarea
    results_dict['faultarea'] = faultarea
    
    #Find center of mass difference in top/bottom planes
    finaldisp = (stackingfaultsystem.atoms.view['pos'][topmap,  cutindex].mean() -
                 stackingfaultsystem.atoms.view['pos'][~topmap, cutindex].mean())

    results_dict['deltadisp'] = finaldisp - initialdisp
    
    return results_dict
    
def relax_sfsystem(lammps_command, system, potential, symbols, mpi_command=None, 
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
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'system.dat', 
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
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    #Write lammps input script
    template_file = 'sfmin.template'
    lammps_script = 'sfmin.in'
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
    
def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    #Read input values from surface model (if given)
    read_stackingfault_model(input_dict)
    
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
    
    input_dict['stackingfault_shift'] = input_dict.get('stackingfault_shift', '0.0 0.0')
    input_dict['stackingfault_shift'] = list(np.asarray(input_dict['stackingfault_shift'].strip().split(), dtype=float))
    
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

def read_stackingfault_model(input_dict):
    """Read/handle parameters associated with the stacking fault"""
    
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
        
        #Load stackingfault_model
        try:
            with open(input_dict['stackingfault_model']) as f:
                input_dict['stackingfault_model'] = DM(f).find('stacking-fault-parameters')
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
        #Extract parameter values from input_dict
        input_dict['stackingfault_model'] = None
        iprPy.input.axes(input_dict)
        iprPy.input.atomshift(input_dict)
        input_dict['stackingfault_planeaxis'] = input_dict.get('stackingfault_planeaxis', 'z')
        input_dict['stackingfault_planepos'] = float(input_dict.get('stackingfault_planepos', 0.5))
        input_dict['stackingfault_shiftvector1'] = list(np.array(input_dict['stackingfault_shiftvector1'].strip().split(), dtype=float))
        input_dict['stackingfault_shiftvector2'] = list(np.array(input_dict['stackingfault_shiftvector2'].strip().split(), dtype=float))
        
def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, input_dict['potential_dir'])
        
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)
    
    input_stackingfault(input_dict)
    
def input_stackingfault(input_dict):
    
    #Check parameter compatibilities
    assert len(input_dict['stackingfault_shiftvector1']) == 3, 'invalid stackingfault_shiftvector1'
    assert len(input_dict['stackingfault_shiftvector2']) == 3, 'invalid stackingfault_shiftvector2'
    assert len(input_dict['stackingfault_shift']) == 2,                                                 'invalid stackingfault_shift'
    assert input_dict['stackingfault_shift'][0] >= 0.0 and input_dict['stackingfault_shift'][0] <= 1.0, 'invalid stackingfault_shift'
    assert input_dict['stackingfault_shift'][1] >= 0.0 and input_dict['stackingfault_shift'][1] <= 1.0, 'invalid stackingfault_shift'
    
    #Pull important parameters out of input_dict
    axes_array = np.array([input_dict['x_axis'], input_dict['y_axis'], input_dict['z_axis']])
    T = am.tools.axes_check(axes_array)
    ucell = input_dict['ucell']
    initialsystem = input_dict['initialsystem']
    sizemults = input_dict['sizemults']
    planepos = input_dict['stackingfault_planepos']
    planeaxis = input_dict['stackingfault_planeaxis']
     
    #Convert from crystallographic axes to Cartesian axes
    vect1 = (input_dict['stackingfault_shiftvector1'][0] * ucell.box.avect + 
             input_dict['stackingfault_shiftvector1'][1] * ucell.box.bvect + 
             input_dict['stackingfault_shiftvector1'][2] * ucell.box.cvect)
    
    vect2 = (input_dict['stackingfault_shiftvector2'][0] * ucell.box.avect + 
             input_dict['stackingfault_shiftvector2'][1] * ucell.box.bvect + 
             input_dict['stackingfault_shiftvector2'][2] * ucell.box.cvect)
    
    #Transform using axes
    vect1 = T.dot(vect1)
    vect2 = T.dot(vect2)
    
    #Calculate planeshift
    input_dict['planeshift'] = input_dict['stackingfault_shift'][0] * vect1 + input_dict['stackingfault_shift'][1] * vect2
    
    #Adjust planepos to be independent of size multipliers

    
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
    output['calculation-stacking-fault'] = calc = DM()
    
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
    
    
    calc['stacking-fault-parameters'] = DM()
    if input_dict['stackingfault_model'] is not None and 'stacking-fault' in input_dict['stackingfault_model']:
        calc['stacking-fault-parameters']['stacking-fault'] = sf = DM()
        sf['key'] = input_dict['stackingfault_model']['stacking-fault']['key']
        sf['id'] =  input_dict['stackingfault_model']['stacking-fault']['id']
    
    calc['stacking-fault-parameters']['system-family'] = input_dict['system_family']
    calc['stacking-fault-parameters']['atomman-stacking-fault-parameters'] = asfp = DM()    
    asfp['crystallographic-axes'] = DM()
    asfp['crystallographic-axes']['x-axis'] = input_dict['x_axis']
    asfp['crystallographic-axes']['y-axis'] = input_dict['y_axis']
    asfp['crystallographic-axes']['z-axis'] = input_dict['z_axis']
    asfp['atomshift'] =      input_dict['atomshift']
    asfp['plane-axis'] =     input_dict['stackingfault_planeaxis']
    asfp['plane-position'] = input_dict['stackingfault_planepos']
    asfp['shift-vector-1'] = input_dict['stackingfault_shiftvector1']
    asfp['shift-vector-2'] = input_dict['stackingfault_shiftvector2']
    
    calc['stacking-fault-shift'] = DM()
    calc['stacking-fault-shift']['shift-vector-fraction'] = input_dict['stackingfault_shift']
    calc['stacking-fault-shift']['Cartesian-vector'] = DM()
    calc['stacking-fault-shift']['Cartesian-vector']['value'] = list(uc.get_in_units(input_dict['planeshift'], 
                                                                input_dict['length_unit']))
    calc['stacking-fault-shift']['Cartesian-vector']['unit'] =  input_dict['length_unit']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:        
        #Save the stacking fault energy
        calc['stacking-fault-energy'] = DM()
        calc['stacking-fault-energy']['value'] = uc.get_in_units(results_dict['stackingfault_energy'], 
                                                 input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')
        calc['stacking-fault-energy']['unit'] =  input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2'
        calc['change-in-plane-separation'] = DM()
        calc['change-in-plane-separation']['value'] = uc.get_in_units(results_dict['deltadisp'], 
                                                      input_dict['length_unit'])
        calc['change-in-plane-separation']['unit'] =  input_dict['length_unit']

    return output
        
if __name__ == '__main__':
    main(*sys.argv[1:])     
    
