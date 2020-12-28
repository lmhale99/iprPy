from copy import deepcopy
from multiprocessing import Pool
from pathlib import Path
from datetime import date

import numpy as np

import atomman.lammps as lmp

import iprPy

from iprPy.workflow import prepare, process, fix_lammps_versions

from iprPy.tools import aslist

############################### Global parameters ##############################

# *database_name* is the name of the saved database settings to use for
# preparing the calculations

# *run_location* specifies the machines that the calculations are to be
# performed on.  This allows for machine-specific executables to be defined
# below in the corresponding section and automatically set later.

# *test_commands* indicates if the machine-specific LAMMPS commands are tested
# prior to preparing the calculations.

# *global_kwargs* are global settings to use with all calculations - not sure
# there are any that work on all...

# *pot_kwargs* are global settings that limit which potential(s) are included
# when preparing.  

# Specify machine and set database
database_name = 'iprhub'
run_location = 'ruth'
test_commands = True

# Generic settings for all calcs
global_kwargs = {}

# Potential-based modifiers
pot_kwargs = {}
pot_kwargs['status'] = 'all'
#pot_kwargs['id'] = ['2020--Starikov-S--Si-Au-Al--LAMMPS--ipr1']
#pot_kwargs['pair_style'] = ['eam', 'eam/alloy', 'eam/fs', 'eam/cd']

########################### Calculation parameters #############################

# *np_per_runner* is number of processors that each prepared calculation will
# expect. It determines the mpi_command to call LAMMPS with for most
# calculations, and should be the number of processors assigned to the
# associated runners.

# *run_directory_name* indicates which directory calculations are prepared in.
# All calcs in the directory should be prepared with the same np_per_runner.
# This allows for different pools of calculations to be created.

# *fix_lammps_versions* indicates if the fix_lammps_versions() function is to
# be called after preparing the calculation.  Ideally, this should only be
# True for the last calculation prepared in any given run_directory.

calc_settings = {}

style = 'isolated_atom'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_3'
calc_settings[style]['fix_lammps_versions'] = False

style = 'diatom_scan'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_3'
calc_settings[style]['fix_lammps_versions'] = False

style = 'E_vs_r_scan'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_3'
calc_settings[style]['fix_lammps_versions'] = True

style = 'relax_box'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_4'
calc_settings[style]['fix_lammps_versions'] = False

style = 'relax_dynamic'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_4'
calc_settings[style]['fix_lammps_versions'] = False

style = 'relax_static'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_4'
calc_settings[style]['fix_lammps_versions'] = True

style = 'relax_static_from_dynamic'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_5'
calc_settings[style]['fix_lammps_versions'] = True

style = 'crystal_space_group'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_6'
calc_settings[style]['fix_lammps_versions'] = True

style = 'elastic_constants_static'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_7'
calc_settings[style]['fix_lammps_versions'] = False

style = 'phonon'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_7'
calc_settings[style]['fix_lammps_versions'] = False

style = 'surface_energy_static'
calc_settings[style] = {}
calc_settings[style]['np_per_runner'] = 1
calc_settings[style]['run_directory_name'] = f'{database_name}_7'
calc_settings[style]['fix_lammps_versions'] = True

#style = 'stacking_fault_map_2D'
#calc_settings[style] = {}
#calc_settings[style]['np_per_runner'] = 1
#calc_settings[style]['run_directory_name'] = f'{database_name}_8'
#calc_settings[style]['fix_lammps_versions'] = True

#style = 'dislocation_monopole'
#calc_settings[style] = {}
#calc_settings[style]['np_per_runner'] = 16
#calc_settings[style]['run_directory_name'] = f'{database_name}_9'
#calc_settings[style]['fix_lammps_versions'] = False

#style = 'dislocation_periodic_array'
#calc_settings[style] = {}
#calc_settings[style]['np_per_runner'] = 16
#calc_settings[style]['run_directory_name'] = f'{database_name}_9'
#calc_settings[style]['fix_lammps_versions'] = True

########################## Machine-specific commands ###########################

allcommands = {}

commands = allcommands['desktop'] = {}
commands['mpi_command'] = 'mpiexec -localonly {np_per_runner}' 
commands['lammps_command'] = 'E:/LAMMPS/2020-03-03/bin/lmp_mpi'
commands['lammps_command_snap_1'] = 'E:/LAMMPS/2017-01-27/bin/lmp_mpi'
commands['lammps_command_snap_2'] = 'E:/LAMMPS/2019-06-05/bin/lmp_mpi'
commands['lammps_command_old'] = 'E:/LAMMPS/2019-06-05/bin/lmp_mpi'

commands = allcommands['laptop'] = {}
commands['mpi_command'] = 'C:/Program Files/MPICH2/bin/mpiexec -localonly {np_per_runner}' 
commands['lammps_command_snap_1'] = 'C:/Program Files/LAMMPS/2017-01-27/bin/lmp_mpi'
commands['lammps_command_snap_2'] = 'C:/Program Files/LAMMPS/2019-06-05/bin/lmp_mpi'
commands['lammps_command_old'] = 'C:/Program Files/LAMMPS/2019-06-05/bin/lmp_mpi'

commands = allcommands['ruth'] = {}
commands['mpi_command'] = '/cluster/deb9/bin/mpirun -n {np_per_runner}' 
commands['lammps_command'] = 'lmp_mpi'
commands['lammps_command_snap_1'] = '/users/lmh1/LAMMPS/bin/lmp_mpi_2017_03_31'
commands['lammps_command_snap_2'] = '/users/lmh1/LAMMPS/bin/lmp_mpi_2019_06_05'
commands['lammps_command_old'] = '/users/lmh1/LAMMPS/bin/lmp_mpi_2019_06_05'
commands['lammps_command_aenet'] = '/users/lmh1/LAMMPS/bin/lmp_mpi_2020_03_03_aenet'
commands['lammps_command_kim'] = '/users/lmh1/LAMMPS/bin/lmp_mpi_2020_03_03_kim'

# Select commands for the machine in use
commands = allcommands[run_location]
global_kwargs['lammps_command'] = commands['lammps_command']

############################# Test LAMMPS commands ############################

if test_commands:
    
    # Test main LAMMPS command
    lammps_command = commands['lammps_command']
    lammpsdate = lmp.checkversion(lammps_command)['date']
    assert lammpsdate >= date(2019, 10, 30)

    # Define test for older LAMMPS commands
    def test_old(commands, key, startdate=None, enddate=None):
        if key in commands:
            command = commands[key]
        else:
            return True

        try:
            lammpsdate = lmp.checkversion(command)['date']
        except:
            print(f'{key} not found or not working')
        else:
            if startdate is not None and lammpsdate < startdate:
                print(f'{key} too old')
            elif enddate is not None and lammpsdate > enddate:
                print(f'{key} too new')
            else:
                return True
        return False

    # Test older LAMMPS commands
    if not test_old(commands, 'lammps_command_snap_1', date(2014,  8,  8), date(2017,  5, 30)):
        del commands['lammps_command_snap_1']
    if not test_old(commands, 'lammps_command_snap_2', date(2018, 12,  3), date(2019,  6, 12)):
        del commands['lammps_command_snap_2']
    if not test_old(commands, 'lammps_command_old', None, date(2019, 10, 30)):   
        del commands['lammps_command_old']

################################ isolated_atom ################################

style = 'isolated_atom'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)
    for key in pot_kwargs:
        kwargs[f'intpot_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.isolated_atom.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

################################## diatom_scan ##################################

style = 'diatom_scan'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['maximum_r'] = '10.0',
    kwargs['number_of_steps_r'] = '500'
    for key in pot_kwargs:
        kwargs[f'potential_{key}'] = pot_kwargs[key]
    
    # Prepare
    prepare.diatom_scan.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

################################## E_vs_r_scan ##################################

style = 'E_vs_r_scan'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    for key in pot_kwargs:
        kwargs[f'prototype_potential_{key}'] = pot_kwargs[key]

    # Prepare bop
    pair_style = kwargs.pop('prototype_potential_pair_style', None)
    if pair_style is None or 'bop' in pair_style:
        try:
            prepare.E_vs_r_scan.bop(database_name, run_directory_name, **kwargs)
        except:
            print('No bops to give')

    # Prepare everything else
    if pair_style is not None:
        kwargs['prototype_potential_pair_style'] = pair_style
    prepare.E_vs_r_scan.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

################################## relax_box ##################################

style = 'relax_box'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)
    
    kwargs['parent_status'] = 'finished'
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key] 
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.relax_box.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

################################ relax_dynamic ################################

style = 'relax_dynamic'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['parent_status'] = 'finished'
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key] 
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
    
    # Prepare
    prepare.relax_dynamic.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

################################# relax_static ################################

style = 'relax_static'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['parent_status'] = 'finished'
    for key in pot_kwargs:
        kwargs[f'reference_potential_{key}'] = pot_kwargs[key] 
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.relax_static.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)


########################## relax_static_from_dynamic ##########################

style = 'relax_static_from_dynamic'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['archive_status'] = 'finished'
    for key in pot_kwargs:
        kwargs[f'archive_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.relax_static.from_dynamic(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

############################# crystal_space_group #############################

style = 'crystal_space_group'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['relax_static_status'] = 'finished'
    kwargs['relax_box_status'] = 'finished'

    # Prepare
    prepare.crystal_space_group.prototype(database_name, run_directory_name, **kwargs)
    prepare.crystal_space_group.reference(database_name, run_directory_name, **kwargs)
    prepare.crystal_space_group.relax(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

########################### elastic_constants_static ##########################

style = 'elastic_constants_static'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['parent_standing'] = 'good'
    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.elastic_constants_static.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

#################################### phonon ###################################

style = 'phonon'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    kwargs['parent_method'] = 'dynamic'
    kwargs['parent_standing'] = 'good'

    # Prepare
    prepare.phonon.main(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

############################ surface_energy_static ############################

style = 'surface_energy_static'
if style in calc_settings:
    database = iprPy.load_database(database_name)

    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs for each family
    families = np.unique(database.get_records_df(style='free_surface').family)
    for family in families:
        print(family)
        kwargs = deepcopy(global_kwargs)
        if np_per_runner > 1:
            kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)
        
        kwargs['parent_method'] = 'dynamic'
        kwargs['parent_standing'] = 'good'
        kwargs['parent_family'] = kwargs['defect_family'] = family 
        for key in pot_kwargs:
            kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
        
        # Prepare
        try:
            prepare.surface_energy_static.main(database_name, run_directory_name, **kwargs)
        except:
            print('0 record combinations to check')

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

############################ stacking_fault_map_2D ############################

style = 'stacking_fault_map_2D'
if style in calc_settings:
    database = iprPy.load_database(database_name)

    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs for each family
    families = np.unique(database.get_records_df(style='stacking_fault').family)
    for family in families:
        print(family)
        kwargs = deepcopy(global_kwargs)
        if np_per_runner > 1:
            kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)
        
        kwargs['parent_method'] = 'dynamic'
        kwargs['parent_standing'] = 'good'
        kwargs['parent_family'] = kwargs['defect_family'] = family
        for key in pot_kwargs:
            kwargs[f'parent_potential_{key}'] = pot_kwargs[key]
        
        # Prepare
        try:
            prepare.stacking_fault_map_2D.main(database_name, run_directory_name, **kwargs)
        except:
            print('0 record combinations to check')

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

############################# dislocation_monopole ############################

style = 'dislocation_monopole'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.dislocation_monopole.bcc_screw(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.bcc_edge(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.bcc_edge_112(database_name, run_directory_name, **kwargs)
    prepare.dislocation_monopole.fcc_edge_100(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)

########################## dislocation_periodic_array #########################

style = 'dislocation_periodic_array'
if style in calc_settings:
    
    # Load settings
    np_per_runner = calc_settings[style]['np_per_runner']
    run_directory_name = calc_settings[style]['run_directory_name']
    
    # Build kwargs
    kwargs = deepcopy(global_kwargs)
    if np_per_runner > 1:
        kwargs['mpi_command'] = commands['mpi_command'].format(np_per_runner=np_per_runner)

    for key in pot_kwargs:
        kwargs[f'parent_potential_{key}'] = pot_kwargs[key]

    # Prepare
    prepare.dislocation_periodic_array.fcc_edge_mix(database_name, run_directory_name, **kwargs)
    prepare.dislocation_periodic_array.fcc_screw(database_name, run_directory_name, **kwargs)

    # Fix LAMMPS versions
    if calc_settings[style]['fix_lammps_versions']:
        fix_lammps_versions(run_directory_name, commands)
