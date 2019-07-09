



# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys
import uuid
import glob
import shutil
import datetime
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

import matplotlib.pyplot as plt

record_style = 'calculation_point_defect_mobility'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    d = datetime.datetime.today()
    d = d.replace(microsecond=0)
    d = d.replace(second=0)
    fileNameTime = d.strftime('%Y-%m-%d_%H%M')
    fileNameSymbols = ''
    for x in input_dict['allSymbols']:
        fileNameSymbols = fileNameSymbols+'_'+x
    fileName = fileNameTime + fileNameSymbols
    
    
    
    sourcedir = os.path.join(os.getcwd())
    
        # If workingdir is already set, then do nothing (already in correct folder)
    try:
        workingdir = workingdir

    # Change to workingdir if not already there
    except:
        workingdir = os.path.join(os.getcwd(), 'calculationfiles', record_style)
        if not os.path.isdir(workingdir):
            os.makedirs(workingdir)
        os.chdir(workingdir)

    try:
        stroagedir = stroagedir

    # Change to workingdir if not already there
    except:
        storagedir = os.path.join(workingdir,fileName)
        if not os.path.isdir(storagedir):
            os.makedirs(storagedir)
        os.chdir(storagedir)
        
    #script = os.path.splitext(os.path.basename(__file__))[0]
    #print(script)
    #record = iprPy.load_record(record_style)
    
    shutil.copyfile(sourcedir+'\\calc_point_defect_mobility.in', storagedir+'\\calc_point_defect_mobility.in')
    
    results_dict = DM()
    
    results_dict['neb_log'] = calc_neb(input_dict['lammps_command'],
                            input_dict['initialsystem'],
                            input_dict['potential'],
                            input_dict['pointdefect_number'],
                            input_dict['defectpair_number'],
                            input_dict['point_kwargs'],
                            input_dict['defect_pairs'],
                            input_dict['allSymbols'],
                            sourcedir,
                            mpi_command = input_dict['mpi_command'],
                            etol = input_dict['energytolerance'], #From lammps_min
                            ftol = input_dict['forcetolerance'], #From lammps_min
                            dmax = input_dict['maxatommotion'], #From lammps_min
                            nreplicas = input_dict['numberreplicas'],  #New Thing
                            springconst = input_dict['springconstant'], #New Thing
                            thermosteps = input_dict['thermosteps'],  #New Thing
                            dumpsteps = input_dict['dumpsteps'], #New Thing
                            timestep = input_dict['timestep'], #New Thing
                            minsteps = input_dict['minsteps'], #New Thing
                            climbsteps = input_dict['climbsteps'] #New Thing
                            )

#Following are values to parse for in a future interpret function for neb systems


    neb = lmp.NEBLog()
    
    
    print('There were', neb.nreplicas, 'replicas')
    print(neb.minrun)
    print(neb.climbrun)
    
    fig = plt.figure()
    
    rx, e = neb.get_neb_path(0)

    
    results_dict['unrelaxed_run'] = DM() 
    results_dict['unrelaxed_run']['coordinates'] = rx.tolist()
    results_dict['unrelaxed_run']['energy'] = e.tolist()
    
    plt.plot(rx, e, 'o:', label='unrelaxed')

    rx, e = neb.get_neb_path(neb.minrun.Step.values[-1])
    
    results_dict['final_minimized_run'] = DM() 
    results_dict['final_minimized_run']['coordinates'] = rx.tolist()
    results_dict['final_minimized_run']['energy'] = e.tolist()
    
    plt.plot(rx, e, 'o:',label='after min run')

    rx, e = neb.get_neb_path(neb.climbrun.Step.values[-1])
    
    plt.plot(rx, e, 'o:',label='after climb run')

    results_dict['final_climb_run'] = DM() 
    results_dict['final_climb_run']['coordinates'] = rx.tolist()
    results_dict['final_climb_run']['energy'] = e.tolist()

    plt.legend()
    
    plt.title('Defect Formation energy vs Normalized Migration Coordinate')
    plt.xlabel('Migration Coordinate')
    plt.ylabel('Change in formation energy (eV)')
    
    
    fig.savefig('EnergyvsCoord.png')
    
    
    
    fig2 = plt.figure()
    
    rx1, e1 = neb.get_neb_path(neb.minrun.Step.values[-1])
    rx2, e2 = neb.get_neb_path(neb.climbrun.Step.values[-1])
    
    
    rx = []
    e = []
    index1 = 0
    index2 = 0
    
    while index2 < len(rx2):
        if rx1[index1] < rx2[index2]:
            rx.append(rx1[index1])
            e.append(e1[index1])
            index1 = index1+1
        elif rx1[index1] > rx2[index2]:
            rx.append(rx2[index2])
            e.append(e2[index2])
            index2 = index2+1
        elif rx1[index1]==rx2[index1]:
            rx.append(rx1[index1])
            e.append(e1[index1])
            index1 = index1+1
            index2 = index2+1
    
    results_dict['min_and_climb_run'] = DM() 
    results_dict['min_and_climb_run']['coordinates'] = rx
    results_dict['min_and_climb_run']['energy'] = e
    
    plt.plot(rx, e, 'o:',label='Min and Climb Run Combined')
    plt.legend()
    
    plt.title('Defect Formation energy vs Normalized Migration Coordinate')
    plt.xlabel('Migration Coordinate')
    plt.ylabel('Change in formation energy (eV)')
    
    
    fig2.savefig('min_climb_combined.png')
    
    
    print('Forward barrier =', uc.get_in_units(neb.get_barrier(), 'eV'), 'eV')
    print('Reverse barrier =', uc.get_in_units(neb.get_barrier(reverse=True), 'eV'), 'eV')
    
    script = os.path.splitext(os.path.basename(__file__))[0]
    
    results_dict['barrier'] = DM()
    results_dict['barrier']['energy_units'] = 'eV'
    results_dict['barrier']['forward_barrier'] = uc.get_in_units(neb.get_barrier(), 'eV')
    results_dict['barrier']['reverse_barrier'] = uc.get_in_units(neb.get_barrier(reverse=True), 'eV')
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)
    
def calc_neb(lammps_command, system_info, potential, point_defect_number, defect_pair_number,point_kwargs,
             defect_pair_info, allSymbols, sourcedir, mpi_command = None, etol=0.0, ftol=1e-4, dmax =uc.set_in_units(0.01, 'angstrom'),
             nreplicas=11, springconst = 5, thermosteps = 100,
             dumpsteps = 10000, timestep = 0.01, minsteps = 10000,
             climbsteps = 10000):

    #Section for making alterations to the overall simulation structure
    
    system = system_info
    
    
    for defectIndex in range(int(point_defect_number)):
        for pairIndex in range(int(defect_pair_number)):
            pairKey = 'defectpair_'+str(pairIndex+1)
            startNum = defect_pair_info[pairIndex][0]
            endNum = defect_pair_info[pairIndex][1]
            startNum = int(startNum)
            endNum = int(endNum)
            if ((defectIndex != startNum) and (defectIndex != endNum)):
                if point_kwargs[defectIndex]['ptd_type'].lower() == 'v':
                    system = am.defect.vacancy(system, pos=point_kwargs[defectIndex]['pos'])
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 'i':
                    system = am.defect.interstitial(system, pos=point_kwargs[defectIndex]['pos'],atype = point_kwargs[defectIndex]['atype'])
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 's':
                    system = am.defect.substitutional(system, pos=point_kwargs[defectIndex]['pos'],atype = point_kwargs[defectIndex]['atype'])
                else:
                    system = am.defect.dumbbell(system, pos=point_kwargs[defectIndex]['pos'],db_vect=point_kwargs[defectIndex]['db_vect'])
    currentSymbols = []
    
    for x in range(system.natypes):
        currentSymbols.append(allSymbols[x])
    
    system.symbols = currentSymbols
    
    start_system = system

    for defectIndex in range(int(point_defect_number)):
        for pairIndex in range(int(defect_pair_number)):
            pairKey = 'defectpair_'+str(pairIndex+1)
            startNum = defect_pair_info[pairIndex][0]
            endNum = defect_pair_info[pairIndex][1]
            startNum = int(startNum)
            endNum = int(endNum)
            if (defectIndex == startNum):
                if point_kwargs[defectIndex]['ptd_type'].lower() == 'v':
                    start_system = am.defect.vacancy(start_system, pos=point_kwargs[endNum]['pos'])
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 'i':
                    start_system = am.defect.interstitial(start_system, pos=point_kwargs[defectIndex]['pos'],atype = point_kwargs[defectIndex]['atype'])
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 'db':
                    start_system = am.defect.dumbbell(start_system, pos=point_kwargs[defectIndex]['pos'],db_vect=point_kwargs[defectIndex]['db_vect'])
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 's':
                    raise ValueError('substitutional defects are not implemented for this situation')
                else:
                    raise ValueError('Invalid Defect Type')
    
    currentSymbols = []
    for x in range(start_system.natypes):
        currentSymbols.append(allSymbols[x])
    start_system.symbols = currentSymbols
    start_system_atoms = start_system.atoms
    start_natoms = start_system.natoms

    start_system_info = start_system.dump('atom_data', f='init.dat')
    
    
    final_system = start_system
    movedAtomIndexes = []
    for defectIndex in range(int(point_defect_number)):
        for pairIndex in range(int(defect_pair_number)):
            pairKey = 'defectpair_'+str(pairIndex+1)
            startNum = defect_pair_info[pairIndex][0]
            endNum = defect_pair_info[pairIndex][1]
            startNum = int(startNum)
            endNum = int(endNum)
            if (defectIndex == endNum):
                if point_kwargs[defectIndex]['ptd_type'].lower() == 'v':
                    for x in range(start_natoms):
                        xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs[startNum]['pos'][0],3)
                        yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs[startNum]['pos'][1],3)
                        zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs[startNum]['pos'][2],3)
                        if ((xPos and yPos) and zPos):
                            final_system.atoms.pos[x] = point_kwargs[endNum]['pos']
                            movedAtomIndexes.append(x)
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 'i':
                    for x in range(start_natoms):
                        xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs[startNum]['pos'][0],3)
                        yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs[startNum]['pos'][1],3)
                        zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs[startNum]['pos'][2],3)
                        if ((xPos and yPos) and zPos):
                            final_system.atoms.pos[x] = point_kwargs[endNum]['pos']
                            movedAtomIndexes.append(x)
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 'db':
                    for x in range(start_natoms):
                        xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs[startNum]['pos'][0]-point_kwargs[startNum]['db_vect'][0],3)
                        yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs[startNum]['pos'][1]-point_kwargs[startNum]['db_vect'][1],3)
                        zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs[startNum]['pos'][2]-point_kwargs[startNum]['db_vect'][2],3)
                        if ((xPos and yPos) and zPos):
                            final_system.atoms.pos[x] = point_kwargs[startNum]['pos']
                            movedAtomIndexes.append(x)
                    for y in range(start_natoms):
                        xPos = round(start_system_atoms.pos[y,0],3) == round(point_kwargs[startNum]['pos'][0]+point_kwargs[startNum]['db_vect'][0],3)
                        yPos = round(start_system_atoms.pos[y,1],3) == round(point_kwargs[startNum]['pos'][1]+point_kwargs[startNum]['db_vect'][1],3)
                        zPos = round(start_system_atoms.pos[y,2],3) == round(point_kwargs[startNum]['pos'][2]+point_kwargs[startNum]['db_vect'][2],3)
                        if ((xPos and yPos) and zPos):
                            final_system.atoms.pos[y] = point_kwargs[endNum]['pos']-point_kwargs[endNum]['db_vect']
                            movedAtomIndexes.append(y)
                    for z in range(start_natoms):
                        xPos = round(start_system_atoms.pos[z,0],3) == round(point_kwargs[endNum]['pos'][0],3)
                        yPos = round(start_system_atoms.pos[z,1],3) == round(point_kwargs[endNum]['pos'][1],3)
                        zPos = round(start_system_atoms.pos[z,2],3) == round(point_kwargs[endNum]['pos'][2],3)
                        if ((xPos and yPos) and zPos):
                            final_system.atoms.pos[z] = point_kwargs[endNum]['pos']+point_kwargs[endNum]['db_vect']
                            movedAtomIndexes.append(z)
                elif point_kwargs[defectIndex]['ptd_type'].lower() == 's':
                    raise ValueError('substitutional defects are not implemented for this situation')
                else:   
                    raise ValueError('Invalid Defect Type')
    
    final_system_pos = final_system.atoms.pos[movedAtomIndexes]
    movedAtomIds = [x+1 for x in movedAtomIndexes]

    with open('final.dat', 'w') as f:
        f.write('%i\n' % len(movedAtomIds))
        for x in range(len(movedAtomIds)):
            f.write('%i ' % movedAtomIds[x])
            for y in range(len(final_system_pos[x])):
                f.write('%.13f ' % final_system_pos[x][y])
            f.write('\n')
    
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_terms = {}
    lammps_terms['nreplicas'] = nreplicas
    lammps_terms['springconst'] = springconst
    lammps_terms['thermosteps'] = thermosteps
    lammps_terms['dumpsteps'] = dumpsteps
    lammps_terms['timestep'] = timestep
    lammps_terms['minsteps'] = minsteps
    lammps_terms['climbsteps'] = climbsteps
    lammps_terms['dmax'] = dmax
    lammps_terms['etol'] = etol
    lammps_terms['ftol'] = ftol
    lammps_terms['atomman_system_info'] = start_system_info
    lammps_terms['atomman_pair_info'] = potential.pair_info(start_system.symbols)
    lammps_terms['final_system'] = 'final.dat'
    
    # Write lammps input script
    template_file = sourcedir+'\\neb_lammps.template'
    input_file = 'neb_lammps.in'
    with open(template_file) as f:
        template = f.read()

    with open(input_file, 'w') as f:
        f.write(am.tools.filltemplate(template, lammps_terms, '<', '>'))
        
    output = lmp.run(lammps_command, 'neb_lammps.in', mpi_command=mpi_command)
    neb = lmp.NEBLog()
    
    return neb

def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    
    # Set calculation UUID
    if UUID is not None:
        input_dict['calc_key'] = UUID
    else:
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.interpret('units', input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '5 5 5')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    input_dict['numberreplicas'] = input_dict.get('numberreplicas', '11')
    input_dict['springconst'] = input_dict.get('numberreplicas', '5')
    input_dict['thermosteps'] = input_dict.get('thermosteps','100')
    input_dict['timestep'] = input_dict.get('timestep', '0.01')
    input_dict['dumpsteps'] = input_dict.get('dumpsteps', '10000')
    input_dict['minsteps'] = input_dict.get('minimumsteps', '10000')
    input_dict['climbsteps'] = input_dict.get('climbsteps', '10000')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # input_dict['key'] = int(input_dict.get('key', default))
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    #Using lammps_minimize to gather most of the information about
    iprPy.input.interpret('lammps_minimize', input_dict)
    
    # Check lammps_command and mpi_command
    iprPy.input.interpret('lammps_commands', input_dict)
    
    # Load potential
    iprPy.input.interpret('lammps_potential', input_dict)
    
    # Load the initial system
    iprPy.input.interpret('atomman_systemload', input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.interpret('atomman_systemmanipulate', input_dict, build=build)
    
    #Using pointdefect to define initial and final positions for atoms in the strucutre
    
    iprPy.input.interpret('pointdefect', input_dict, build=build)

    input_dict['defectpair_number'] = input_dict.get('defectpair_number', '0')
    
    if int(input_dict['defectpair_number']) > 0:
        defect_pairs = {}
        input_dict['defect_pairs']={}
        for y in range(int(input_dict['defectpair_number'])):
            pairKey = 'defectpair_'+str(y+1)
            defect_pairs[pairKey] = input_dict.get(pairKey)
            input_dict['defect_pairs'][y] = {}
            input_dict['defect_pairs'][y][0],input_dict['defect_pairs'][y][1] = defect_pairs[pairKey].split(' ')
    else:
        input_dict['defect_pairs'] = None

    
    input_dict['allSymbols'] = input_dict.get('allSymbols', input_dict['symbols']).split(' ')
            
if __name__ == '__main__':
    main(*sys.argv[1:])
