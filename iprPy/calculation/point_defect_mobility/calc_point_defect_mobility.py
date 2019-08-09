


# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
from pathlib import Path
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
    
    results_dict = DM()    
    
    results_dict['neb_log'] = calc_neb( input_dict['lammps_command'],
                                        input_dict['initialsystem'],
                                        input_dict['potential'],
                                        input_dict['initialdefect_number'],
                                        input_dict['defectpair_number'],
                                        input_dict['point_mobility_kwargs'],
                                        input_dict['allSymbols'],
                                        mpi_command = input_dict['mpi_command'],
                                        etol = input_dict['energytolerance'], #From lammps_min
                                        ftol = input_dict['forcetolerance'], #From lammps_min
                                        dmax = input_dict['maxatommotion'], #From lammps_min
                                        nreplicas = input_dict['numberreplicas'],  #For NEB
                                        springconst = input_dict['springconst'], #For NEB
                                        thermosteps = input_dict['thermosteps'],  #For NEB
                                        dumpsteps = input_dict['dumpsteps'], # For minimization settings
                                        timestep = input_dict['timestep'], # For minimization setings 
                                        minsteps = input_dict['minsteps'], #For NEB
                                        climbsteps = input_dict['climbsteps'] #For NEB
                                        )

    
    # Load log from completed NEB
    
    neb = lmp.NEBLog()
    
    #Printing the number of replicas, and the log for the minruns and climbruns
    
    print('There were', neb.nreplicas, 'replicas')
    print(neb.minrun)
    print(neb.climbrun)
    
    #Creating a figure which contains the energy vs movement coordinate information
    #for the initial system, the final minimized system, and the climbed system
    
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
    
    #Creating a figure which combines the minimum energy path after the 
    #minimization step and the climb steps, to give the fullest description 
    #of the minimum energy path 
    
    fig2 = plt.figure()
    
    rx1, e1 = neb.get_neb_path(neb.minrun.Step.values[-1])
    rx2, e2 = neb.get_neb_path(neb.climbrun.Step.values[-1])
    
    
    rx = []
    e = []
    index1 = 0
    index2 = 0
    
    while index2 < len(rx2):            #Going through the coordinates of the  
        if rx1[index1] < rx2[index2]:   #minimum and climb steps so that they
            rx.append(rx1[index1])      #are properly ordered    
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
    
    #Storing and ploting resulting information
    
    results_dict['min_and_climb_run'] = DM()
    results_dict['min_and_climb_run']['coordinates'] = rx
    results_dict['min_and_climb_run']['energy'] = e
    
    plt.plot(rx, e, 'o:',label='Min and Climb Run Combined')
    plt.legend()
    
    plt.title('Defect Formation energy vs Normalized Migration Coordinate')
    plt.xlabel('Migration Coordinate')
    plt.ylabel('Change in formation energy (eV)')
    
    #Creating a record using the calc_point_defect_mobility format
    
    record = iprPy.load_record(record_style)    
    
    fig2.savefig('min_climb_combined.png')
    
    #Printing the information on the forward and reverse energy barrier,
    #and storing it in the results dict
    
    print('Forward barrier =', uc.get_in_units(neb.get_barrier(), 'eV'), 'eV')
    print('Reverse barrier =', uc.get_in_units(neb.get_barrier(reverse=True), 'eV'), 'eV')
    
    script = os.path.splitext(os.path.basename(__file__))[0]
    
    results_dict['barrier'] = DM()
    results_dict['barrier']['energy_units'] = 'eV'
    results_dict['barrier']['forward_barrier'] = uc.get_in_units(neb.get_barrier(), 'eV')
    results_dict['barrier']['reverse_barrier'] = uc.get_in_units(neb.get_barrier(reverse=True), 'eV')
    
    #building a record and printing it
    
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)


    
def calc_neb(lammps_command, system_info, potential, initial_defect_number,
             defect_pair_number,defect_mobility_kwargs, allSymbols, mpi_command = None,
             etol=0.0, ftol=1e-4, dmax =uc.set_in_units(0.01, 'angstrom'),
             nreplicas=11, springconst = 5, thermosteps = 100,
             dumpsteps = 10000, timestep = 0.01, minsteps = 10000,
             climbsteps = 10000):

    #Section for making alterations to the overall simulation structure
    
    #Defining the initial perfect system using the original info
    
    initial_system = system_info
    
    #Adding defects to the system which will stay in the same position during the simulation
    
    for defectIndex in range(int(initial_defect_number)):
        point_kwargs = defect_mobility_kwargs['initial'][defectIndex]
        if point_kwargs['ptd_type'].lower() == 'v':
            initial_system = am.defect.vacancy(initial_system, pos=point_kwargs['pos'])
        elif point_kwargs['ptd_type'].lower() == 'i':
            initial_system = am.defect.interstitial(initial_system, pos=point_kwargs['pos'],atype = point_kwargs['atype'])
        elif point_kwargs['ptd_type'].lower() == 's':
            initial_system = am.defect.substitutional(initial_system, pos=point_kwargs['pos'],atype = point_kwargs['atype'])
        elif point_kwargs['ptd_type'].lower() == 'db':
            initial_system = am.defect.dumbbell(initial_system, pos=point_kwargs['pos'],db_vect=point_kwargs['db_vect'])
        else:
            raise ValueError('Invalid Defect Type')
    currentSymbols = []
    
    for x in range(initial_system.natypes):  #Checking to see if the alteration of the system has added any new atom types
        currentSymbols.append(allSymbols[x]) #and adding the appropriate symbols for those new atoms 
    
    initial_system.symbols = currentSymbols
    
    #Adding moving defects to the system in their start position
    
    start_system = initial_system

    for defectIndex in range(int(defect_pair_number)):
        point_kwargs = defect_mobility_kwargs['start'][defectIndex]
        if point_kwargs['ptd_type'].lower() == 'v':
            start_system = am.defect.vacancy(start_system, pos=point_kwargs['pos'])
        elif point_kwargs['ptd_type'].lower() == 'i':
            start_system = am.defect.interstitial(start_system, pos=point_kwargs['pos'],atype = point_kwargs['atype'])
        elif point_kwargs['ptd_type'].lower() == 'db':
            start_system = am.defect.dumbbell(start_system, pos=point_kwargs['pos'],db_vect=point_kwargs['db_vect'])
        elif point_kwargs['ptd_type'].lower() == 's':
            print('not implemented for subsutitutional defect type.  To simulate a substitutional vacancy jump, define the position of a subsitutional atom in the initial system, and make the end position of the vacancy the same position as the subsitutional')
        else:
            raise ValueError('Invalid Defect Type')
    
    #Checking again to see if symbols need to be added
    
    currentSymbols = []  
    for x in range(start_system.natypes):
        currentSymbols.append(allSymbols[x])
    
    #Creating a list of atoms in the start system which the next segment uses to find the atom id for atoms in a certain position
    
    start_system.symbols = currentSymbols
    start_system_atoms = start_system.atoms
    start_natoms = start_system.natoms

    #Dumps the start system to be used for NEB simulations

    start_system_info = start_system.dump('atom_data', f='init.dat')
    
    #Check to see which defect type is being used, finding the position of that atom, extracting
    #the atom id, and then generating a list of new positions used to define the final system for
    #the neb simulation
    
    final_system = start_system
    movedAtomIndexes = []
    for defectIndex in range(int(defect_pair_number)):
        point_kwargs = defect_mobility_kwargs['end'][defectIndex] #End kwargs, used to define the end positions
        point_kwargs_start = defect_mobility_kwargs['start'][defectIndex] #Start kwargs, used to find the original position of the atoms
        if point_kwargs['ptd_type'].lower() == 'v':
            for x in range(start_natoms):
                xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs['pos'][0],3)
                yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs['pos'][1],3)
                zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs['pos'][2],3)
                if ((xPos and yPos) and zPos):
                    final_system.atoms.pos[x] = point_kwargs_start['pos']
                    movedAtomIndexes.append(x)
        elif point_kwargs['ptd_type'].lower() == 'i':
            for x in range(start_natoms):
                xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs_start['pos'][0],3)
                yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs_start['pos'][1],3)
                zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs_start['pos'][2],3)
                if ((xPos and yPos) and zPos):
                    final_system.atoms.pos[x] = point_kwargs['pos']
                    movedAtomIndexes.append(x)
        elif point_kwargs['ptd_type'].lower() == 's':
            print('not implemented for subsutitutional defect type.  To simulate a substitutional vacancy jump, define the position of a subsitutional atom in the initial system, and make the end position of the vacancy the same position as the subsitutional')
        elif point_kwargs['ptd_type'].lower() == 'db':
            for x in range(start_natoms):
                xPos = round(start_system_atoms.pos[x,0],3) == round(point_kwargs_start['pos'][0]-point_kwargs_start['db_vect'][0],3)
                yPos = round(start_system_atoms.pos[x,1],3) == round(point_kwargs_start['pos'][1]-point_kwargs_start['db_vect'][1],3)
                zPos = round(start_system_atoms.pos[x,2],3) == round(point_kwargs_start['pos'][2]-point_kwargs_start['db_vect'][2],3)
                if ((xPos and yPos) and zPos):
                    final_system.atoms.pos[x] = point_kwargs['pos']
                    movedAtomIndexes.append(x)
            for y in range(start_natoms):
                xPos = round(start_system_atoms.pos[y,0],3) == round(point_kwargs_start['pos'][0]+point_kwargs_start['db_vect'][0],3)
                yPos = round(start_system_atoms.pos[y,1],3) == round(point_kwargs_start['pos'][1]+point_kwargs_start['db_vect'][1],3)
                zPos = round(start_system_atoms.pos[y,2],3) == round(point_kwargs_start['pos'][2]+point_kwargs_start['db_vect'][2],3)
                if ((xPos and yPos) and zPos):
                    final_system.atoms.pos[y] = point_kwargs['pos']-point_kwargs['db_vect']
                    movedAtomIndexes.append(y)
            for z in range(start_natoms):
                xPos = round(start_system_atoms.pos[z,0],3) == round(point_kwargs['pos'][0],3)
                yPos = round(start_system_atoms.pos[z,1],3) == round(point_kwargs['pos'][1],3)
                zPos = round(start_system_atoms.pos[z,2],3) == round(point_kwargs['pos'][2],3)
                if ((xPos and yPos) and zPos):
                    final_system.atoms.pos[z] = point_kwargs['pos']+point_kwargs['db_vect']
                    movedAtomIndexes.append(z)
        else:   
            raise ValueError('Invalid Defect Type')
    
    final_system_pos = final_system.atoms.pos[movedAtomIndexes]
    movedAtomIds = [x+1 for x in movedAtomIndexes]
    
    #Writing the final position of the moving atoms to be used in the final system
    
    with open('final.dat', 'w') as f:
        f.write('%i\n' % len(movedAtomIds))
        for x in range(len(movedAtomIds)):
            f.write('%i ' % movedAtomIds[x])
            for y in range(len(final_system_pos[x])):
                f.write('%.13f ' % final_system_pos[x][y])
            f.write('\n')
    
    #Get script's location
    script_dir = Path(__file__).parent
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
    
    # Set dump_modify_format based on lammps_date
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_terms['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e %.13e %.13e %.13e"'
    else:
        lammps_terms['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = Path(script_dir, 'neb_lammps.template')
    input_file = 'neb_lammps.in'
    with open(template_file) as f:
        template = f.read()

    with open(input_file, 'w') as f:
        f.write(am.tools.filltemplate(template, lammps_terms, '<', '>'))
    
    #Running the calc_neb    
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

    iprPy.input.subset('units').interpret(input_dict)

    # These are calculation-specific default strings
    input_dict['numberreplicas'] = input_dict.get('numberreplicas', '8')
    input_dict['springconst'] = input_dict.get('springconst', '5')
    input_dict['thermosteps'] = input_dict.get('thermosteps','50')
    input_dict['timestep'] = input_dict.get('timestep', '0.01')
    input_dict['dumpsteps'] = input_dict.get('dumpsteps', '10000')
    input_dict['minsteps'] = input_dict.get('minsteps', '10000')
    input_dict['climbsteps'] = input_dict.get('climbsteps', '10000')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    # None for this calculation

    #Using lammps_minimize to gather most of the information about
    iprPy.input.subset('lammps_minimize').interpret(input_dict)
    
    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)

    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)

    # Load the initial system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)

    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)

    #Using pointdefect to define initial and final positions for atoms in the strucutre
    
    iprPy.input.subset('pointdefectmobility').interpret(input_dict, build=build)
    
    
    
if __name__ == '__main__':
    main(*sys.argv[1:])
